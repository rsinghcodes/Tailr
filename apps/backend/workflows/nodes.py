import json
import logging
import re
from typing import Any
from workflows.state import WorkflowState
from domain.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_llm: LLMProvider | None = None


def _get_llm() -> LLMProvider:
    global _llm
    if _llm is None:
        from infrastructure.langchain.llm_provider import GeminiProvider

        _llm = GeminiProvider()
    return _llm


def _record_step(state: WorkflowState, step: str) -> None:
    telemetry = state.get("telemetry", {})
    telemetry["current_step"] = step
    telemetry["step_history"] = list(telemetry.get("step_history", [])) + [step]
    state["telemetry"] = telemetry


def _safe_json(obj: Any) -> str:
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return str(obj)


def _extract_json(text: str) -> dict | list | None:
    if not text or not text.strip():
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"```(?:json)?\s*", "", cleaned).strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r",\s*([\]}])", r"\1", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    return None


def _format_feedback(state: WorkflowState) -> str:
    """Format user feedback into an instruction block for the rewrite prompt."""
    if not isinstance(state, dict):
        return ""
    feedback = state.get("user_feedback")
    if not isinstance(feedback, dict):
        return ""

    sections: list[str] = []
    items = feedback.get("items") or []
    for item in items:
        if not isinstance(item, dict):
            continue
        comment = str(item.get("comment") or "").strip()
        if not comment:
            continue
        bullet = str(item.get("bullet") or "").strip()
        company = str(item.get("company") or "").strip()
        role = str(item.get("role") or "").strip()
        location = f" ({role} at {company})" if role and company else f" ({role})" if role else ""
        sections.append(f"- \"{bullet}\"{location}: {comment}")

    global_comment = str(feedback.get("global_comment") or "").strip()
    if global_comment:
        sections.append(f"- Overall: {global_comment}")

    if not sections:
        return ""

    return (
        "User Feedback — modify ONLY the content referenced below. Every other "
        "bullet point, the summary, skills, projects, and education must stay "
        "exactly as provided in the Resume: same text, same order. Do not reword, "
        "reorder, add, or remove anything else:\n"
        + "\n".join(sections)
    )


def _norm_lower(text: Any) -> str:
    return " ".join(str(text or "").lower().split())


def _experience_key(exp: dict[str, Any]) -> str:
    company = str(exp.get("company") or "").strip().lower()
    role = str(exp.get("role") or "").strip().lower()
    return f"{company}|{role}"


def _bullet_texts(bullets: Any) -> list[str]:
    if not isinstance(bullets, list):
        bullets = [bullets]
    return [
        b.get("text") if isinstance(b, dict) else str(b or "")
        for b in bullets
    ]


def _apply_feedback_lock(
    original: Any,
    rewritten: Any,
    feedback: Any,
) -> Any:
    """Restore every un-commented piece of content after a feedback rewrite.

    When user feedback is present, the rewrite must touch ONLY the bullets the
    user commented on. Everything else — the summary (unless a summary-level
    comment exists), skills, projects, education, and every un-commented
    experience bullet — is locked back to the canonical resume so re-optimizing
    never rewrites bullets the user did not comment on.
    """
    if not isinstance(original, dict) or not isinstance(rewritten, dict):
        return rewritten
    if not isinstance(feedback, dict):
        return rewritten

    items = [it for it in (feedback.get("items") or []) if isinstance(it, dict)]
    if not items:
        return rewritten

    has_summary_feedback = any(
        not str(it.get("company") or "").strip()
        and not str(it.get("role") or "").strip()
        for it in items
    )

    commented_per_exp: dict[str, set[str]] = {}
    for it in items:
        company = str(it.get("company") or "").strip()
        role = str(it.get("role") or "").strip()
        if not company and not role:
            continue
        key = f"{company.lower()}|{role.lower()}"
        commented_per_exp.setdefault(key, set()).add(_norm_lower(it.get("bullet")))

    locked = json.loads(json.dumps(rewritten))

    for section in ("skills", "projects", "education"):
        locked[section] = original.get(section)

    if not has_summary_feedback:
        locked["summary"] = original.get("summary")

    original_exp = [
        e for e in (original.get("experience") or []) if isinstance(e, dict)
    ]
    rewritten_exp = [
        e for e in (locked.get("experience") or []) if isinstance(e, dict)
    ]
    rewritten_by_key = {_experience_key(e): e for e in rewritten_exp}

    locked_exp: list[dict[str, Any]] = []
    for orig in original_exp:
        key = _experience_key(orig)
        exp = rewritten_by_key.get(key, orig)
        canonical_bullets = _bullet_texts(orig.get("bullets"))
        commented = commented_per_exp.get(key, set())

        if not commented:
            locked_exp.append(
                {**exp, "bullets": [{"text": b} for b in canonical_bullets]}
            )
            continue

        new_bullets = _bullet_texts(exp.get("bullets"))
        rebuilt: list[dict[str, Any]] = []
        for idx, canonical_bullet in enumerate(canonical_bullets):
            if _norm_lower(canonical_bullet) in commented and idx < len(new_bullets):
                rebuilt.append({"text": new_bullets[idx]})
            else:
                rebuilt.append({"text": canonical_bullet})
        locked_exp.append({**exp, "bullets": rebuilt})

    locked["experience"] = locked_exp
    return locked


async def retrieve_context_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "RETRIEVAL")
    logger.info("Retrieving context from vector store")

    try:
        from infrastructure.llamaindex.vector_store import VectorStoreService

        vector_store = VectorStoreService()

        resume = state.get("canonical_resume", {}) or {}
        jd = state.get("job_requirements", {}) or {}
        query_parts = []
        if resume.get("summary"):
            query_parts.append(resume["summary"])
        if resume.get("skills"):
            query_parts.append(", ".join(s["name"] for s in resume["skills"] if isinstance(s, dict)))
        if jd.get("title"):
            query_parts.append(jd["title"])
        if jd.get("required_skills"):
            query_parts.append(", ".join(jd["required_skills"]))
        if jd.get("responsibilities"):
            query_parts.append(" ".join(jd["responsibilities"]))
        query = " ".join(query_parts)[:500] if query_parts else "resume optimization context"

        context = await vector_store.query_context(query, top_k=5)
        return {"retrieved_context": context}

    except Exception as exc:
        logger.warning("Vector store retrieval failed: %s", str(exc))
        return {"retrieved_context": "No relevant context found."}


async def plan_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "PLANNING")
    logger.info("Generating rewrite plan with LLM")

    llm = _get_llm()

    resume_json = _safe_json(state.get("canonical_resume", {}))
    jd_json = _safe_json(state.get("job_requirements", {}))
    context = state.get("retrieved_context", "")

    try:
        system_prompt = (
            "You are an expert technical resume strategist. "
            "Analyze the resume and job requirements to build a structured optimization plan. "
            "Do NOT rewrite text. Only generate the strategy. "
            "Return valid JSON with: target_sections (list of strings), strategy (string). "
            "Never invent experiences, skills, or achievements."
        )

        user_prompt = (
            f"Resume:\n{resume_json}\n\n"
            f"Job Requirements:\n{jd_json}\n\n"
            f"Retrieved Context:\n{context}\n\n"
            "Generate an optimization plan."
        )

        result = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        parsed = _extract_json(result) if isinstance(result, str) else result

        rewrite_plan = {
            "target_sections": parsed.get("target_sections", ["summary", "experience"]) if parsed else ["summary", "experience"],
            "strategy": parsed.get("strategy", "Optimize for job match") if parsed else "Default optimization strategy",
        }

        return {"rewrite_plan": rewrite_plan}

    except Exception as exc:
        logger.warning("LLM planning failed: %s", str(exc))
        return {
            "rewrite_plan": {
                "target_sections": ["summary", "experience"],
                "strategy": "Default optimization strategy",
            }
        }


async def rewrite_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "REWRITING")
    logger.info("Rewriting resume with LLM")

    llm = _get_llm()

    resume_json = _safe_json(state.get("canonical_resume", {}))
    plan_json = _safe_json(state.get("rewrite_plan", {}))
    context = state.get("retrieved_context", "")

    try:
        system_prompt = (
            "You are a professional technical resume writer. "
            "Rewrite the candidate's resume based on the provided optimization plan. "
            "Do NOT invent any skills, technologies, projects, or metrics. "
            "Preserve all employment dates, titles, and company names exactly. "
            "Improve readability, action verbs, and keyword alignment. "
            "Return valid JSON matching the resume schema."
        )

        user_prompt = (
            f"Resume:\n{resume_json}\n\n"
            f"Rewrite Plan:\n{plan_json}\n\n"
            f"Retrieved Context:\n{context}\n\n"
        )
        feedback_text = _format_feedback(state)
        if feedback_text:
            user_prompt += f"{feedback_text}\n\n"
        user_prompt += "Rewrite the resume implementing the plan."

        result = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        parsed = _extract_json(result) if isinstance(result, str) else result

        original = state.get("canonical_resume", {})
        rewritten_resume = {
            "summary": (parsed.get("summary", original.get("summary", "")) if parsed else original.get("summary", "")),
            "skills": (parsed.get("skills", original.get("skills", [])) if parsed else original.get("skills", [])),
            "experience": (parsed.get("experience", original.get("experience", [])) if parsed else original.get("experience", [])),
            "projects": (parsed.get("projects", original.get("projects", [])) if parsed else original.get("projects", [])),
            "education": (parsed.get("education", original.get("education", [])) if parsed else original.get("education", [])),
        }
        rewritten_resume = _apply_feedback_lock(
            original, rewritten_resume, state.get("user_feedback")
        )

        return {"rewritten_resume": rewritten_resume}

    except Exception as exc:
        logger.warning("LLM rewriting failed, returning original: %s", str(exc))
        return {"rewritten_resume": state.get("canonical_resume")}


async def guardrails_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "GUARDRAILS")
    logger.info("Running guardrails engine")

    try:
        from guardrails.pipeline import GuardrailsEngine
        from guardrails.base import GuardrailContext

        engine = GuardrailsEngine()
        rewritten = state.get("rewritten_resume") or {}
        content = _safe_json(rewritten)
        context = GuardrailContext(
            canonical_resume=state.get("canonical_resume"),
            job_description=state.get("job_requirements"),
        )

        result = await engine.execute(content, context)

        guardrail_report = {
            "status": result.status.value,
            "repaired": result.repair_applied or getattr(result, "repaired", False),
            "violations": [v.model_dump(mode="json") for v in result.violations]
            if result.violations
            else [],
            "repaired_content": getattr(result, "repaired_content", None),
            "warnings": result.warnings,
            "metadata": result.metadata,
        }

        result_data: dict[str, Any] = {"guardrail_report": guardrail_report}
        if result.repaired_content:
            try:
                repaired = (
                    json.loads(result.repaired_content)
                    if isinstance(result.repaired_content, str)
                    else result.repaired_content
                )
                result_data["rewritten_resume"] = repaired
            except (json.JSONDecodeError, TypeError):
                pass

        return result_data

    except Exception as exc:
        logger.warning("Guardrails execution failed: %s", str(exc))
        return {
            "guardrail_report": {
                "status": "error",
                "repaired": False,
                "violations": [],
                "warnings": [str(exc)],
                "metadata": {},
            }
        }


async def validation_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "VALIDATING")
    logger.info("Running business validation")

    canonical = state.get("canonical_resume") or {}
    rewritten = state.get("rewritten_resume") or {}
    violations = []
    warnings = []

    if not rewritten.get("summary"):
        warnings.append("No summary found in rewritten resume")

    if not rewritten.get("experience"):
        warnings.append("No experience entries found in rewritten resume")

    if not rewritten.get("skills"):
        warnings.append("No skills found in rewritten resume")

    if canonical.get("summary") and rewritten.get("summary"):
        if len(rewritten["summary"]) < 20:
            warnings.append("Summary is very short")

    checks_run = 4
    status = "PASSED" if not violations else "FAILED"

    return {
        "validation_report": {
            "status": status,
            "checks_run": checks_run,
            "violations": violations,
            "warnings": warnings,
        }
    }


async def ats_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "ATS_ANALYSIS")
    logger.info("Running ATS analysis with LLM")

    llm = _get_llm()

    rewritten_json = _safe_json(state.get("rewritten_resume", {}))
    jd_json = _safe_json(state.get("job_requirements", {}))

    try:
        system_prompt = (
            "You are an ATS analyzer. Evaluate the resume against job requirements. "
            "Return valid JSON with: score (0-100), keyword_coverage (0-1), "
            "strengths (list), weaknesses (list), missing_keywords (list), "
            "recommendations (list)."
        )

        result = await llm.generate(
            prompt=f"Resume:\n{rewritten_json}\n\nJob Requirements:\n{jd_json}\n\nAnalyze ATS compatibility.",
            system_prompt=system_prompt,
        )

        parsed = _extract_json(result) if isinstance(result, str) else result

        ats_report = {
            "score": parsed.get("score", 0) if parsed else 0,
            "keyword_coverage": parsed.get("keyword_coverage", 0) if parsed else 0,
            "strengths": parsed.get("strengths", []) if parsed else [],
            "weaknesses": parsed.get("weaknesses", []) if parsed else [],
            "missing_keywords": parsed.get("missing_keywords", []) if parsed else [],
            "recommendations": parsed.get("recommendations", []) if parsed else [],
        }

        return {"ats_report": ats_report}

    except Exception as exc:
        logger.warning("LLM ATS analysis failed: %s", str(exc))
        return {
            "ats_report": {
                "score": 0,
                "keyword_coverage": 0,
                "strengths": [],
                "weaknesses": [],
                "missing_keywords": [],
                "recommendations": [],
            }
        }


async def render_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "RENDERING")
    logger.info("Rendering final output")

    rewritten = state.get("rewritten_resume") or {}
    return {"render_result": _safe_json(rewritten)}
