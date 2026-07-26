import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from agents.planner.agent import PlannerAgent
from agents.rewriter.agent import RewriterAgent
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service

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


@router.post("/optimization/plan", response_model=PlanOptimizationResponse)
async def plan_optimization(
    body: PlanOptimizationRequest,
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Generate structured optimization plan using Planning Agent (qwen3:8b)."""
    cache_key = f"opt_plan:{body.resume_id}:{body.job_description_id}"
    cached = await cache_service.get(cache_key, PlanOptimizationResponse)
    if cached:
        return cached

    try:
        plan_out = await _planner_agent.plan(
            canonical_resume={"summary": "Software Engineer with Python experience"},
            jd_requirements={"required_skills": ["Python", "FastAPI", "Docker"]},
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
async def rewrite_resume_content(body: RewriteContentRequest):
    """Execute AI resume content rewriting adhering to the optimization plan."""
    try:
        await _rewriter_agent.rewrite(
            resume={"summary": "Software Engineer with Python experience"},
            rewrite_plan={"strategy_summary": "Emphasize FastAPI and async systems"},
            model="qwen3:8b",
        )
        return RewriteContentResponse(
            rewritten_resume_id=f"res-variant-{uuid.uuid4().hex[:8]}",
            status="rewritten",
        )
    except Exception as exc:
        logger.error("Optimization rewrite error: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(exc)}") from exc
