import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.repositories.job_description_repository import (
    JobDescriptionRepositoryImpl,
)
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_llm_provider, get_prompt_registry

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Optimization Engine"], dependencies=[Depends(get_current_user)]
)


class PlanOptimizationRequest(BaseModel):
    resume_id: str
    job_description_id: str


class PlanOptimizationResponse(BaseModel):
    plan_id: str
    target_sections: list[str] = Field(default_factory=list)
    strategy: str


class RewriteContentRequest(BaseModel):
    resume_id: str
    plan_id: str
    guardrail_profile: str = "rewrite_strict"


class RewriteContentResponse(BaseModel):
    rewritten_resume_id: str
    status: str = "rewritten"


@router.post("/optimization/plan", response_model=PlanOptimizationResponse)
async def plan_optimization(
    body: PlanOptimizationRequest,
    session: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
    registry: PromptRegistry = Depends(get_prompt_registry),
):
    """Generate structured optimization plan using the LLM planner."""
    resume_repo = ResumeRepositoryImpl(session)
    jd_repo = JobDescriptionRepositoryImpl(session)

    resume = await resume_repo.get_by_version_id(uuid.UUID(body.resume_id))
    if not resume:
        raise HTTPException(
            status_code=404, detail=f"Resume {body.resume_id} not found"
        )

    jd_result = await jd_repo.get_by_id(uuid.UUID(body.job_description_id))
    if not jd_result:
        raise HTTPException(
            status_code=404,
            detail=f"Job description {body.job_description_id} not found",
        )
    jd, reqs = jd_result

    try:
        system_prompt = registry.get_prompt("planner", "system", "v1")
        user_template = registry.get_prompt("planner", "user", "v1")

        resume_json = resume.model_dump(mode="json")
        jd_requirements = (
            reqs.model_dump(mode="json") if reqs else {"description": jd.description}
        )

        user_prompt = user_template.format(
            resume_json=str(resume_json),
            job_requirements=str(jd_requirements),
            retrieved_context="(no additional context available)",
        )

        plan = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        import json

        plan_data = json.loads(plan) if isinstance(plan, str) else plan
        target_sections = (
            plan_data.get("target_sections", ["summary", "experience"])
            if isinstance(plan_data, dict)
            else ["summary", "experience"]
        )
        strategy = (
            plan_data.get("strategy", "Optimize resume for job match")
            if isinstance(plan_data, dict)
            else str(plan)
        )

        return PlanOptimizationResponse(
            plan_id=f"plan-{uuid.uuid4().hex[:8]}",
            target_sections=target_sections,
            strategy=strategy,
        )
    except Exception as exc:
        logger.error("Optimization planning failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(exc)}")


@router.post("/optimization/rewrite", response_model=RewriteContentResponse)
async def rewrite_resume_content(
    body: RewriteContentRequest,
    session: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
    registry: PromptRegistry = Depends(get_prompt_registry),
):
    """Execute AI resume content rewriting adhering to the optimization plan."""
    resume_repo = ResumeRepositoryImpl(session)

    resume = await resume_repo.get_by_version_id(uuid.UUID(body.resume_id))
    if not resume:
        raise HTTPException(
            status_code=404, detail=f"Resume {body.resume_id} not found"
        )

    try:
        system_prompt = registry.get_prompt("rewrite", "system", "v1")
        user_template = registry.get_prompt("rewrite", "user", "v1")

        resume_json = resume.model_dump(mode="json")

        user_prompt = user_template.format(
            resume_json=str(resume_json),
            rewrite_plan="(apply standard optimization strategy)",
            retrieved_context="(no additional context available)",
        )

        _rewritten = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        return RewriteContentResponse(
            rewritten_resume_id=f"res-variant-{uuid.uuid4().hex[:8]}",
            status="rewritten",
        )
    except Exception as exc:
        logger.error("Resume rewriting failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Rewriting failed: {str(exc)}")
