from typing import Optional
from domain.resume.models import Resume
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from agents.planner.agent import PlannerOutput


class RewriterAgent:
    """Agent that rewrites resume contents according to a structured plan."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def rewrite(
        self,
        resume: Resume,
        plan: PlannerOutput,
        retrieved_context: list[str],
        model: Optional[str] = None,
        temperature: float = 0.4,
    ) -> Resume:
        """Rewrites the candidate resume JSON based on the Planner's recommendations."""
        system_prompt = self.prompt_registry.get_prompt("rewrite", "system", "v1")
        user_template = self.prompt_registry.get_prompt("rewrite", "user", "v1")

        resume_json = resume.model_dump_json(indent=2)
        plan_json = plan.model_dump_json(indent=2)
        context_str = "\n".join(f"- {c}" for c in retrieved_context)

        user_prompt = user_template.format(
            resume_json=resume_json,
            rewrite_plan=plan_json,
            retrieved_context=context_str,
        )

        rewritten_resume: Resume = await self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=Resume,
            temperature=temperature,
            model=model,
        )
        return rewritten_resume
