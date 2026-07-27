import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from infrastructure.database import get_db
from infrastructure.repositories.workflow_repository import WorkflowRepositoryImpl
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service
from infrastructure.database.workflow_models import WorkflowRunModel
from infrastructure.database.resume_models import ResumeModel
from infrastructure.database.guardrail_models import GuardrailEventModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["History & Analytics"])


class WorkflowHistoryItem(BaseModel):
    workflow_id: str
    resume_title: str
    job_title: str
    status: str
    ats_score: float
    created_at: str


class HistoryResponse(BaseModel):
    workflows: list[WorkflowHistoryItem] = Field(default_factory=list)
    total: int = 0


class AnalyticsDashboardResponse(BaseModel):
    total_optimizations: int = 0
    average_ats_improvement: float = 0.0
    guardrail_pass_rate: float = 1.0
    total_resumes: int = 0


@router.get("/history", response_model=HistoryResponse)
async def get_optimization_history(
    session: AsyncSession = Depends(get_db),
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Retrieve optimization workflow history from database."""
    cache_key = "history:all"
    cached = await cache_service.get(cache_key, HistoryResponse)
    if cached:
        return cached

    items = []
    try:
        stmt = (
            select(WorkflowRunModel)
            .order_by(WorkflowRunModel.created_at.desc())
            .limit(50)
        )
        result = await session.execute(stmt)
        runs = result.scalars().all()

        for r in runs:
            # Try to get resume title
            resume_title = "Master Resume"
            if r.resume_id:
                try:
                    res_stmt = select(ResumeModel.title).where(ResumeModel.id == r.resume_id)
                    res_result = await session.execute(res_stmt)
                    title_row = res_result.scalar_one_or_none()
                    if title_row:
                        resume_title = title_row
                except Exception:
                    pass

            # Extract ATS score from state_data
            ats_score = 0.0
            if r.state_data and isinstance(r.state_data, dict):
                ats_data = r.state_data.get("ats_report")
                if isinstance(ats_data, dict):
                    ats_score = ats_data.get("overall_score", 0.0)

            items.append(
                WorkflowHistoryItem(
                    workflow_id=str(r.id),
                    resume_title=resume_title,
                    job_title="Target Position",
                    status=r.status or "UNKNOWN",
                    ats_score=ats_score,
                    created_at=r.created_at.isoformat() if r.created_at else "",
                )
            )
    except Exception as exc:
        logger.warning("DB workflow history query error: %s", str(exc))

    response = HistoryResponse(workflows=items, total=len(items))
    await cache_service.set(cache_key, response, ttl_seconds=60)
    return response


@router.get("/analytics", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    session: AsyncSession = Depends(get_db),
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Retrieve dashboard analytics and live system metrics."""
    cache_key = "analytics:dashboard"
    cached = await cache_service.get(cache_key, AnalyticsDashboardResponse)
    if cached:
        return cached

    total_optimizations = 0
    total_resumes = 0
    avg_ats = 0.0
    guardrail_pass_rate = 1.0

    try:
        # Count workflows
        wf_count_stmt = select(func.count(WorkflowRunModel.id))
        wf_result = await session.execute(wf_count_stmt)
        total_optimizations = wf_result.scalar() or 0

        # Count resumes
        res_count_stmt = select(func.count(ResumeModel.id))
        res_result = await session.execute(res_count_stmt)
        total_resumes = res_result.scalar() or 0

        # Calculate average ATS score from completed workflows
        if total_optimizations > 0:
            ats_stmt = select(WorkflowRunModel.state_data).where(
                WorkflowRunModel.status == "COMPLETED"
            )
            ats_result = await session.execute(ats_stmt)
            state_rows = ats_result.scalars().all()

            scores = []
            for sd in state_rows:
                if isinstance(sd, dict) and sd.get("ats_report"):
                    score = sd["ats_report"].get("overall_score", 0)
                    if score > 0:
                        scores.append(score)
            if scores:
                avg_ats = round(sum(scores) / len(scores), 1)

        # Calculate guardrail pass rate
        guardrail_count_stmt = select(func.count(GuardrailEventModel.id))
        guardrail_result = await session.execute(guardrail_count_stmt)
        total_events = guardrail_result.scalar() or 0

        if total_events > 0:
            rejected_stmt = select(func.count(GuardrailEventModel.id)).where(
                GuardrailEventModel.severity == "critical"
            )
            rejected_result = await session.execute(rejected_stmt)
            rejected_count = rejected_result.scalar() or 0
            guardrail_pass_rate = round(1.0 - (rejected_count / total_events), 3)

    except Exception as exc:
        logger.warning("Analytics DB query fallback: %s", str(exc))

    response = AnalyticsDashboardResponse(
        total_optimizations=total_optimizations,
        average_ats_improvement=avg_ats,
        guardrail_pass_rate=guardrail_pass_rate,
        total_resumes=total_resumes,
    )
    await cache_service.set(cache_key, response, ttl_seconds=60)
    return response
