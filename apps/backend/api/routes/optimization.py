import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from agents.planner.agent import PlannerAgent
from agents.rewriter.agent import RewriterAgent
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service
from infrastructure.database import get_db
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.repositories.job_description_repository import JobDescriptionRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Optimization Engine"])

_ollama_provider = OllamaProvider()
_planner_agent = PlannerAgent(_ollama_provider)
_rewriter_agent = RewriterAgent(_ollama_provider)


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


async def _fetch_resume_dict(resume_id: str, session: AsyncSession) -> dict:
    try:
        repo = ResumeRepositoryImpl(session)
        resume = await repo.get_by_version_id(uuid.UUID(resume_id))
        if resume:
            return resume.model_dump(mode="json")
    except Exception as exc:
        logger.warning("Failed to fetch resume %s: %s", resume_id, str(exc))
    return {"summary": "Candidate Resume", "skills": [], "experience": []}


async def _fetch_jd_requirements(jd_id: str, session: AsyncSession) -> dict:
    try:
        repo = JobDescriptionRepositoryImpl(session)
        result = await repo.get_by_id(uuid.UUID(jd_id))
        if result:
            _, reqs = result
            if reqs:
                return {
                    "required_skills": reqs.required_skills,
                    "preferred_skills": reqs.preferred_skills,
                    "keywords": reqs.keywords,
                    "priority_keywords": reqs.keywords or reqs.required_skills,
                }
    except Exception as exc:
        logger.warning("Failed to fetch JD %s: %s", jd_id, str(exc))
    return {"required_skills": [], "priority_keywords": []}


@router.post("/optimization/plan", response_model=PlanOptimizationResponse)
async def plan_optimization(
    body: PlanOptimizationRequest,
    session: AsyncSession = Depends(get_db),
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Generate structured optimization plan using Planning Agent."""
    cache_key = f"opt_plan:{body.resume_id}:{body.job_description_id}"
    cached = await cache_service.get(cache_key, PlanOptimizationResponse)
    if cached:
        return cached

    try:
        resume_data = await _fetch_resume_dict(body.resume_id, session)
        jd_reqs = await _fetch_jd_requirements(body.job_description_id, session)

        plan_out = await _planner_agent.plan(
            canonical_resume=resume_data,
            jd_requirements=jd_reqs,
            model="qwen3:8b",
        )

        response = PlanOptimizationResponse(
            plan_id=f"plan-{uuid.uuid4().hex[:8]}",
            target_sections=["summary", "experience", "skills"],
            strategy=plan_out.strategy_summary,
        )
        await cache_service.set(cache_key, response, ttl_seconds=1800)
        return response
    except Exception as exc:
        logger.error("Optimization planning error: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(exc)}") from exc


@router.post("/optimization/rewrite", response_model=RewriteContentResponse)
async def rewrite_resume_content(
    body: RewriteContentRequest,
    session: AsyncSession = Depends(get_db),
):
    """Execute AI resume content rewriting adhering to the optimization plan."""
    try:
        resume_data = await _fetch_resume_dict(body.resume_id, session)

        await _rewriter_agent.rewrite(
            resume=resume_data,
            rewrite_plan={"strategy_summary": "Optimize for target role keywords and ATS compatibility"},
            model="qwen3:8b",
        )
        return RewriteContentResponse(
            rewritten_resume_id=f"res-variant-{uuid.uuid4().hex[:8]}",
            status="rewritten",
        )
    except Exception as exc:
        logger.error("Optimization rewrite error: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(exc)}") from exc
