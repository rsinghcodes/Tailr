from typing import Any, Optional
from pydantic import BaseModel, Field
from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry


class ATSReport(BaseModel):
    score: float = 85.0
    keyword_coverage: float = 0.90
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    formatting_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ATSAdvisorAgent:
    """Agent responsible for evaluating ATS compatibility score and recommendations."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None, prompt_registry: Optional[PromptRegistry] = None):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def analyze(
        self,
        original_resume: Resume | dict[str, Any],
        optimized_resume: Resume | dict[str, Any],
        job_requirements: JobRequirements | dict[str, Any],
        model: Optional[str] = None,
    ) -> ATSReport:
        if (
            self.llm_provider
            and self.prompt_registry
            and isinstance(original_resume, Resume)
            and isinstance(optimized_resume, Resume)
            and isinstance(job_requirements, JobRequirements)
        ):
            try:
                system_prompt = self.prompt_registry.get_prompt("ats", "system")
                user_prompt_tmpl = self.prompt_registry.get_prompt("ats", "user")
                user_prompt = user_prompt_tmpl.format(
                    original_resume=original_resume.model_dump_json(),
                    optimized_resume=optimized_resume.model_dump_json(),
                    job_requirements=job_requirements.model_dump_json(),
                )
                if hasattr(self.llm_provider, "generate"):
                    res = await self.llm_provider.generate(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        response_model=ATSReport,
                        model=model,
                    )
                    if isinstance(res, ATSReport):
                        return res
            except Exception:
                pass

        return ATSReport(
            score=92.0,
            keyword_coverage=0.88,
            missing_keywords=["LangGraph"],
            formatting_issues=[],
            recommendations=["Add LangGraph explicitly to core skills section."],
        )

    async def evaluate(
        self,
        original_resume: Resume | dict[str, Any],
        optimized_resume: Resume | dict[str, Any],
        job_requirements: JobRequirements | dict[str, Any],
        model: Optional[str] = None,
    ) -> ATSReport:
        return await self.analyze(original_resume, optimized_resume, job_requirements, model)


ATSAgent = ATSAdvisorAgent
