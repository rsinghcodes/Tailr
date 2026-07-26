import json
import logging
import re
from typing import Any, Optional
from pydantic import BaseModel, Field
from domain.resume.models import Resume
from domain.job_description.models import JobRequirements
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry

logger = logging.getLogger(__name__)


class PlanItem(BaseModel):
    section: str = "summary"
    action: str = "modify"
    instructions: str = ""
    reasoning: str = ""
    rationale: str = ""
    evidence_citations: list[str] = Field(default_factory=list)


class PlannerOutput(BaseModel):
    strategy_summary: str = "Highlight core engineering achievements and target skills."
    summary: list[PlanItem] = Field(default_factory=list)
    skills: list[PlanItem] = Field(default_factory=list)
    experience: list[PlanItem] = Field(default_factory=list)
    projects: list[PlanItem] = Field(default_factory=list)
    plan_items: list[PlanItem] = Field(default_factory=list)


class PlannerAgent:
    """Agent responsible for generating an evidence-backed optimization plan using AI reasoning."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None, prompt_registry: Optional[PromptRegistry] = None):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry or PromptRegistry()

    async def generate_plan(
        self,
        resume: Resume | dict[str, Any],
        job_requirements: JobRequirements | dict[str, Any],
        retrieved_context: Any = "",
        model: Optional[str] = None,
    ) -> PlannerOutput:
        resume_obj = Resume.model_validate(resume) if isinstance(resume, dict) else resume
        jd_obj = JobRequirements.model_validate(job_requirements) if isinstance(job_requirements, dict) else job_requirements

        if self.llm_provider:
            try:
                system_prompt = (
                    "You are a Senior Technical Resume Planner AI Agent. "
                    "Analyze the candidate's canonical resume and target job requirements. "
                    "Generate a structured section-by-section optimization plan as JSON matching this schema:\n"
                    "- strategy_summary: high-level alignment strategy\n"
                    "- plan_items: list of PlanItem objects with keys: section, action, instructions, reasoning, evidence_citations\n"
                    "Return ONLY valid JSON."
                )

                resume_json = resume_obj.model_dump_json() if hasattr(resume_obj, "model_dump_json") else json.dumps(resume)
                jd_json = jd_obj.model_dump_json() if hasattr(jd_obj, "model_dump_json") else json.dumps(job_requirements)
                user_prompt = f"Canonical Resume:\n{resume_json}\n\nJob Requirements:\n{jd_json}\n\nRetrieved Context:\n{str(retrieved_context)}"

                if hasattr(self.llm_provider, "generate"):
                    res = await self.llm_provider.generate(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        response_model=PlannerOutput,
                        model=model or "qwen3:8b",
                    )
                    if isinstance(res, PlannerOutput):
                        return res
                    if isinstance(res, dict):
                        return PlannerOutput.model_validate(res)
                    if isinstance(res, str):
                        cleaned = re.sub(r"```json\s*", "", res)
                        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
                        return PlannerOutput.model_validate(json.loads(cleaned))
            except Exception as exc:
                logger.warning("LLM planner agent execution failed, using fallback plan: %s", str(exc))

        # Fallback plan generation
        req_skills = getattr(jd_obj, "required_skills", []) or ["Python", "Software Engineering"]
        skills_str = ", ".join(req_skills[:5])
        return PlannerOutput(
            strategy_summary=f"Emphasize experience with {skills_str} and system performance optimization.",
            plan_items=[
                PlanItem(
                    section="summary",
                    action="rewrite_summary",
                    instructions=f"Highlight expertise in {skills_str} and system architecture.",
                    reasoning="Align summary directly with core job requirements.",
                    rationale="Role prioritizes technical stack alignment.",
                    evidence_citations=["Canonical resume work experience"],
                ),
                PlanItem(
                    section="experience",
                    action="quantify_impact",
                    instructions="Incorporate measurable performance metrics and latency improvements.",
                    reasoning="Demonstrates engineering impact.",
                    rationale="High impact bullets increase ATS score.",
                    evidence_citations=["Master resume experience bullets"],
                ),
            ],
        )

    async def plan(
        self,
        canonical_resume: Any,
        jd_requirements: Any,
        context: Any = "",
        model: Optional[str] = None,
    ) -> PlannerOutput:
        return await self.generate_plan(canonical_resume, jd_requirements, context, model)
