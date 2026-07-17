import uuid
from typing import Optional
from pydantic import BaseModel, Field

from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry


class PlanItem(BaseModel):
    target_id: Optional[uuid.UUID] = None
    action: str  # e.g., "reorder", "modify", "emphasize", "remove", "add"
    instructions: str
    reasoning: str


class PlannerOutput(BaseModel):
    summary: list[PlanItem] = Field(default_factory=list)
    skills: list[PlanItem] = Field(default_factory=list)
    experience: list[PlanItem] = Field(default_factory=list)
    projects: list[PlanItem] = Field(default_factory=list)


class PlannerAgent:
    """Agent that determines how to optimize the resume sections based on job requirements and retrieved context."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def plan(
        self,
        resume: Resume,
        job_requirements: JobRequirements,
        retrieved_context: list[str],
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> PlannerOutput:
        """Generates a structured rewrite plan for the resume sections."""
        system_prompt = self.prompt_registry.get_prompt("planner", "system", "v1")
        user_template = self.prompt_registry.get_prompt("planner", "user", "v1")

        resume_json = resume.model_dump_json(indent=2)
        job_reqs_json = job_requirements.model_dump_json(indent=2)
        context_str = "\n".join(f"- {c}" for c in retrieved_context)

        user_prompt = user_template.format(
            resume_json=resume_json,
            job_requirements=job_reqs_json,
            retrieved_context=context_str,
        )

        plan_output: PlannerOutput = await self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=PlannerOutput,
            temperature=temperature,
            model=model,
        )
        return plan_output
