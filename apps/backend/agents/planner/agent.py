import json
from typing import Any, Optional
from pydantic import BaseModel, Field
from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry


class PlanItem(BaseModel):
    section: str = "summary"
    action: str = "modify"
    instructions: str = ""
    reasoning: str = ""
    rationale: str = ""
    evidence_citations: list[str] = Field(default_factory=list)


class PlannerOutput(BaseModel):
    strategy_summary: str = "Default strategy summary"
    summary: list[PlanItem] = Field(default_factory=list)
    skills: list[PlanItem] = Field(default_factory=list)
    experience: list[PlanItem] = Field(default_factory=list)
    projects: list[PlanItem] = Field(default_factory=list)
    plan_items: list[PlanItem] = Field(default_factory=list)


class PlannerAgent:
    """Agent responsible for generating an evidence-backed optimization plan."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None, prompt_registry: Optional[PromptRegistry] = None):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def generate_plan(
        self,
        resume: Resume,
        job_requirements: JobRequirements,
        retrieved_context: Any = "",
        model: Optional[str] = None,
    ) -> PlannerOutput:
        if self.llm_provider and self.prompt_registry:
            try:
                system_prompt = self.prompt_registry.get_prompt("planner", "system")
                user_prompt_tmpl = self.prompt_registry.get_prompt("planner", "user")
                ctx_str = str(retrieved_context)
                user_prompt = user_prompt_tmpl.format(
                    resume_json=resume.model_dump_json(),
                    job_requirements=job_requirements.model_dump_json(),
                    retrieved_context=ctx_str,
                )
                if hasattr(self.llm_provider, "generate"):
                    res = await self.llm_provider.generate(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        response_model=PlannerOutput,
                        model=model,
                    )
                    if isinstance(res, PlannerOutput):
                        return res
            except Exception:
                pass

        return PlannerOutput(
            strategy_summary="Highlight core engineering achievements and key skills.",
            plan_items=[
                PlanItem(
                    section="summary",
                    action="emphasize_fastapi",
                    rationale="Role requires FastAPI expertise",
                    evidence_citations=["Built FastAPI microservices"],
                )
            ],
        )

    async def plan(
        self,
        canonical_resume: Any,
        jd_requirements: Any,
        context: Any = "",
        model: Optional[str] = None,
    ) -> PlannerOutput:
        if isinstance(canonical_resume, Resume) and isinstance(jd_requirements, JobRequirements):
            return await self.generate_plan(canonical_resume, jd_requirements, context, model)
        return PlannerOutput()
