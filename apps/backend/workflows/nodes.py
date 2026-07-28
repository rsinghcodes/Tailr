import json
import logging
from typing import Any
from workflows.state import WorkflowState
from config.settings import settings
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from domain.resume.models import Resume, Skill, Experience, ExperienceBullet
from domain.job_description.models import JobRequirements

logger = logging.getLogger(__name__)

_llm: LLMProvider | None = None
_registry: PromptRegistry | None = None


def _get_llm() -> LLMProvider:
    global _llm
    if _llm is None:
        from infrastructure.langchain.llm_provider import GeminiProvider
        _llm = GeminiProvider()
    return _llm


def _get_registry() -> PromptRegistry:
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry


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


async def parse_resume_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "PARSING")
    logger.info("Parsing resume with LLM")

    raw_text = state.get("raw_resume_text", "")
    if not raw_text:
        return {"canonical_resume": None, "errors": state.get("errors", []) + ["No resume text provided"]}

    llm = _get_llm()
    registry = _get_registry()

    try:
        system_prompt = (
            "You are a resume parser. Extract structured data from the resume text. "
            "Return valid JSON with: summary, skills (list of {name, category}), "
            "experience (list of {company, role, start_date, end_date, bullets: [{text}]}), "
            "projects (list of {title, description, technologies}). "
            "Do NOT invent any information. Only extract what is present in the text."
        )

        result = await llm.generate(
            prompt=f"Parse this resume into structured JSON:\n\n{raw_text}",
            system_prompt=system_prompt,
        )

        parsed = json.loads(result) if isinstance(result, str) else result

        canonical_resume = {
            "summary": parsed.get("summary", raw_text[:500]),
            "skills": parsed.get("skills", []),
            "experience": parsed.get("experience", []),
            "projects": parsed.get("projects", []),
            "education": parsed.get("education", []),
        }

        return {"canonical_resume": canonical_resume}

    except Exception as exc:
        logger.warning("LLM resume parsing failed, using basic extraction: %s", str(exc))
        return {
            "canonical_resume": {
                "summary": raw_text[:500] if len(raw_text) > 500 else raw_text,
                "skills": [],
                "experience": [],
                "projects": [],
                "education": [],
            }
        }


async def parse_jd_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "JD_ANALYSIS")
    logger.info("Analyzing job description with LLM")

    jd_text = state.get("job_description_text", "")
    if not jd_text:
        return {"job_requirements": None}

    llm = _get_llm()

    try:
        system_prompt = (
            "You are a job description analyzer. Extract structured requirements from the JD text. "
            "Return valid JSON with: title, required_skills (list of strings), "
            "preferred_skills (list of strings), responsibilities (list of strings), "
            "keywords (list of strings), experience_level (string). "
            "Do NOT invent any information."
        )

        result = await llm.generate(
            prompt=f"Analyze this job description and extract requirements:\n\n{jd_text}",
            system_prompt=system_prompt,
        )

        parsed = json.loads(result) if isinstance(result, str) else result

        job_requirements = {
            "title": parsed.get("title", ""),
            "required_skills": parsed.get("required_skills", []),
            "preferred_skills": parsed.get("preferred_skills", []),
            "responsibilities": parsed.get("responsibilities", []),
            "keywords": parsed.get("keywords", []),
            "experience_level": parsed.get("experience_level", ""),
        }

        return {"job_requirements": job_requirements}

    except Exception as exc:
        logger.warning("LLM JD analysis failed, using minimal extraction: %s", str(exc))
        return {
            "job_requirements": {
                "title": "",
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "keywords": [],
                "experience_level": "",
            }
        }


async def retrieve_context_node(state: WorkflowState) -> dict[str, Any]:
    _record_step(state, "RETRIEVAL")
    logger.info("Retrieving context from vector store")

    try:
        from infrastructure.llamaindex.client import get_llama_client
        from infrastructure.llamaindex.vector_store import LlamaIndexService

        client = get_llama_client()
        vector_store = LlamaIndexService(client=client)

        resume_text = state.get("raw_resume_text", "")
        jd_text = state.get("job_description_text", "")
        query = f"{resume_text[:200]} {jd_text[:200]}"

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

        parsed = json.loads(result) if isinstance(result, str) else result

        rewrite_plan = {
            "target_sections": parsed.get("target_sections", ["summary", "experience"]),
            "strategy": parsed.get("strategy", "Optimize for job match"),
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
            "Rewrite the resume implementing the plan."
        )

        result = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        parsed = json.loads(result) if isinstance(result, str) else result

        rewritten_resume = {
            "summary": parsed.get("summary", state.get("canonical_resume", {}).get("summary", "")),
            "skills": parsed.get("skills", state.get("canonical_resume", {}).get("skills", [])),
            "experience": parsed.get("experience", state.get("canonical_resume", {}).get("experience", [])),
            "projects": parsed.get("projects", state.get("canonical_resume", {}).get("projects", [])),
            "education": parsed.get("education", state.get("canonical_resume", {}).get("education", [])),
        }

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
        context = GuardrailContext()

        result = await engine.execute(content, context)

        guardrail_report = {
            "status": result.status.value,
            "repaired": result.repair_applied or getattr(result, "repaired", False),
            "violations": [v.model_dump(mode="json") for v in result.violations] if result.violations else [],
            "repaired_content": getattr(result, "repaired_content", None),
            "warnings": result.warnings,
            "metadata": result.metadata,
        }

        return {"guardrail_report": guardrail_report}

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

        parsed = json.loads(result) if isinstance(result, str) else result

        ats_report = {
            "score": parsed.get("score", 0),
            "keyword_coverage": parsed.get("keyword_coverage", 0),
            "strengths": parsed.get("strengths", []),
            "weaknesses": parsed.get("weaknesses", []),
            "missing_keywords": parsed.get("missing_keywords", []),
            "recommendations": parsed.get("recommendations", []),
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
