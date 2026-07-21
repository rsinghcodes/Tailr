import json
from typing import Any, Optional
from pydantic import BaseModel, Field
from domain.resume.models import Resume
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from agents.planner.agent import PlannerOutput


class RewriterAgent:
    """Agent responsible for rewriting resume sections based on plan and evidence."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None, prompt_registry: Optional[PromptRegistry] = None):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def rewrite(
        self,
        resume: Resume | dict[str, Any],
        rewrite_plan: PlannerOutput | dict[str, Any] | None = None,
        retrieved_context: str = "",
        model: Optional[str] = None,
    ) -> Resume:
        if self.llm_provider and self.prompt_registry and isinstance(resume, Resume):
            try:
                system_prompt = self.prompt_registry.get_prompt("rewrite", "system")
                user_prompt_tmpl = self.prompt_registry.get_prompt("rewrite", "user")
                plan_json = rewrite_plan.model_dump_json() if isinstance(rewrite_plan, PlannerOutput) else json.dumps(rewrite_plan or {})
                user_prompt = user_prompt_tmpl.format(
                    resume_json=resume.model_dump_json(),
                    rewrite_plan=plan_json,
                    retrieved_context=retrieved_context,
                )
                if hasattr(self.llm_provider, "generate"):
                    res = await self.llm_provider.generate(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        response_model=Resume,
                        model=model,
                    )
                    if isinstance(res, Resume):
                        return res
            except Exception:
                pass

        if isinstance(resume, Resume):
            return resume

        return Resume.model_validate(resume) if isinstance(resume, dict) else Resume()


RewriteAgent = RewriterAgent
