from typing import Optional
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from domain.job_description.models import JobDescription, JobRequirements


class JobDescriptionAnalyzer:
    """Application service to analyze job description texts and extract structured requirements."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        """Initializes the job description analyzer.

        Args:
            llm_provider: The provider utilized to run LLM operations.
            prompt_registry: The registry containing prompt templates.
        """
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def analyze(
        self,
        jd: JobDescription,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> JobRequirements:
        """Analyzes a job description text to extract structured skills and qualifications.

        Args:
            jd: The domain JobDescription object containing the text.
            model: Optional model override.
            temperature: Sampling temperature (default: 0.0).

        Returns:
            A validated JobRequirements instance containing skills, responsibilities,
            keywords, and experience levels.
        """
        system_prompt = self.prompt_registry.get_prompt("jd_analyzer", "system", "v1")
        user_template = self.prompt_registry.get_prompt("jd_analyzer", "user", "v1")

        user_prompt = user_template.format(
            title=jd.title,
            company=jd.company or "Unknown Company",
            description=jd.description
        )

        requirements: JobRequirements = await self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=JobRequirements,
            temperature=temperature,
            model=model
        )

        return requirements
