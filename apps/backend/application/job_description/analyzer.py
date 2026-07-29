from typing import Optional
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from domain.job_description.models import JobDescription, JobRequirements
from infrastructure.llamaindex.extractors import ExtractedJobRequirements


class JobDescriptionAnalyzer:
    """Application service to analyze job description texts and extract structured requirements."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def analyze(
        self,
        jd: JobDescription,
        model: Optional[str] = None,
        temperature: float = 0.0,
        extracted_requirements: Optional[ExtractedJobRequirements] = None,
    ) -> JobRequirements:
        system_prompt = self.prompt_registry.get_prompt("jd_analyzer", "system", "v1")
        user_template = self.prompt_registry.get_prompt("jd_analyzer", "user", "v1")

        user_prompt = user_template.format(
            title=jd.title,
            company=jd.company or "Unknown Company",
            description=jd.description,
        )

        if extracted_requirements:
            extracted_section = (
                "\n\nAdditional pre-extracted data (use as reference, do not blindly copy):\n"
                f"  Required Skills: {', '.join(extracted_requirements.required_skills)}\n"
                f"  Preferred Skills: {', '.join(extracted_requirements.preferred_skills)}\n"
                f"  Responsibilities: {', '.join(extracted_requirements.responsibilities)}\n"
                f"  Keywords: {', '.join(extracted_requirements.keywords)}\n"
                f"  Seniority: {extracted_requirements.seniority or 'N/A'}"
            )
            user_prompt += extracted_section

        requirements: JobRequirements = await self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=JobRequirements,
            temperature=temperature,
            model=model,
        )

        return requirements
