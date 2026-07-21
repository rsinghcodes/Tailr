from typing import Optional
from pydantic import BaseModel, Field

from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry


class ATSReport(BaseModel):
    score: int = Field(..., ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ATSAdvisorAgent:
    """Agent that evaluates optimized resumes against job requirements to calculate ATS score and suggestions."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def analyze(
        self,
        original_resume: Resume,
        optimized_resume: Resume,
        job_requirements: JobRequirements,
        model: Optional[str] = None,
        temperature: float = 0.5,
    ) -> ATSReport:
        """Compares original and optimized resumes and generates a structured ATS match report."""
        system_prompt = self.prompt_registry.get_prompt("ats", "system", "v1")
        user_template = self.prompt_registry.get_prompt("ats", "user", "v1")

        orig_json = original_resume.model_dump_json(indent=2)
        opt_json = optimized_resume.model_dump_json(indent=2)
        job_reqs_json = job_requirements.model_dump_json(indent=2)

        user_prompt = user_template.format(
            original_resume=orig_json,
            optimized_resume=opt_json,
            job_requirements=job_reqs_json,
        )

        report: ATSReport = await self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=ATSReport,
            temperature=temperature,
            model=model,
        )
        return report
