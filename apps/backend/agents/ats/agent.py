import json
import logging
import re
from typing import Any, Optional
from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.ats.models import ATSReport
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry

logger = logging.getLogger(__name__)


class ATSAdvisorAgent:
    """Agent responsible for evaluating ATS compatibility score, keyword coverage, and recommendations."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None, prompt_registry: Optional[PromptRegistry] = None):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry or PromptRegistry()

    async def analyze(
        self,
        original_resume: Resume | dict[str, Any],
        optimized_resume: Resume | dict[str, Any],
        job_requirements: JobRequirements | dict[str, Any],
        model: Optional[str] = None,
    ) -> ATSReport:
        opt_obj = Resume.model_validate(optimized_resume) if isinstance(optimized_resume, dict) else optimized_resume
        jd_obj = JobRequirements.model_validate(job_requirements) if isinstance(job_requirements, dict) else job_requirements

        # Deterministic keyword & coverage calculation
        req_skills = getattr(jd_obj, "required_skills", []) or []
        pref_skills = getattr(jd_obj, "preferred_skills", []) or []
        prio_keywords = getattr(jd_obj, "priority_keywords", []) or []
        all_target_keywords = list(set(req_skills + pref_skills + prio_keywords))

        # Extract text from optimized resume
        text_content = opt_obj.summary or ""
        if opt_obj.experience:
            for exp in opt_obj.experience:
                text_content += " " + " ".join([b.text if hasattr(b, "text") else str(b) for b in exp.bullets])
        if opt_obj.skills:
            text_content += " " + " ".join([sk.name if hasattr(sk, "name") else str(sk) for sk in opt_obj.skills])

        text_lower = text_content.lower()
        matched_keywords = [kw for kw in all_target_keywords if kw.lower() in text_lower]
        missing_keywords = [kw for kw in all_target_keywords if kw.lower() not in text_lower]

        coverage = len(matched_keywords) / len(all_target_keywords) if all_target_keywords else 0.85
        kw_score = min(100.0, coverage * 100.0)
        skills_score = min(100.0, kw_score + 10.0)
        exp_score = 88.0 if opt_obj.experience else 70.0
        semantic_score = 85.0
        overall_score = round(0.35 * kw_score + 0.35 * skills_score + 0.20 * exp_score + 0.10 * semantic_score, 1)

        # Build density map
        words_count = max(1, len(text_lower.split()))
        density_map = {kw: round(text_lower.count(kw.lower()) / words_count, 3) for kw in matched_keywords[:5]}

        base_report = ATSReport(
            overall_score=overall_score,
            confidence=0.95,
            keyword_score=kw_score,
            semantic_score=semantic_score,
            skills_score=skills_score,
            experience_score=exp_score,
            keyword_coverage=round(coverage, 2),
            missing_keywords=missing_keywords[:5],
            keyword_density=density_map,
            strengths=[f"Matched core skills: {', '.join(matched_keywords[:4])}"],
            weaknesses=[f"Missing keywords: {', '.join(missing_keywords[:3])}"] if missing_keywords else [],
            recommendations=[f"Incorporate missing keyword '{kw}' into skills or experience bullets." for kw in missing_keywords[:2]],
        )

        if self.llm_provider:
            try:
                system_prompt = (
                    "You are an ATS Advisor AI Agent. "
                    "Evaluate the candidate resume against job requirements and return structured ATS analysis as JSON matching ATSReport schema."
                )
                user_prompt = (
                    f"Optimized Resume:\n{opt_obj.model_dump_json()}\n\n"
                    f"Job Requirements:\n{jd_obj.model_dump_json()}\n\n"
                    f"Calculated Coverage: {coverage:.2f}"
                )
                if hasattr(self.llm_provider, "generate"):
                    res = await self.llm_provider.generate(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        response_model=ATSReport,
                        model=model or "qwen3:8b",
                    )
                    if isinstance(res, ATSReport):
                        return res
                    if isinstance(res, dict):
                        return ATSReport.model_validate(res)
                    if isinstance(res, str):
                        cleaned = re.sub(r"```json\s*", "", res)
                        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
                        return ATSReport.model_validate(json.loads(cleaned))
            except Exception as exc:
                logger.warning("LLM ATS agent execution failed, returning calculated report: %s", str(exc))

        return base_report

    async def evaluate(
        self,
        original_resume: Resume | dict[str, Any],
        optimized_resume: Resume | dict[str, Any],
        job_requirements: JobRequirements | dict[str, Any],
        model: Optional[str] = None,
    ) -> ATSReport:
        return await self.analyze(original_resume, optimized_resume, job_requirements, model)


ATSAgent = ATSAdvisorAgent
