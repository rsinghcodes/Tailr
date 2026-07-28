import logging
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from infrastructure.database.workflow_models import WorkflowRunModel
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
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    """Retrieve optimization workflow history from the database."""
    stmt = (
        select(WorkflowRunModel)
        .order_by(WorkflowRunModel.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    runs = result.scalars().all()

    items = []
    for run in runs:
        state_data = run.state_data or {}
        ats_report = state_data.get("ats_report") or {}
        ats_score = ats_report.get("score", 0.0) if isinstance(ats_report, dict) else 0.0

        resume_title = ""
        if run.resume and run.resume.title:
            resume_title = run.resume.title

        job_title = ""
        if run.job_description and run.job_description.title:
            job_title = run.job_description.title

        items.append(WorkflowHistoryItem(
            workflow_id=str(run.id),
            resume_title=resume_title,
            job_title=job_title,
            status=run.status,
            ats_score=float(ats_score),
            created_at=run.created_at.isoformat() if run.created_at else "",
        ))

    return HistoryResponse(workflows=items, total=len(items))


@router.get("/analytics", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    session: AsyncSession = Depends(get_db),
):
    """Compute real analytics from the database."""
    total_opt = await session.execute(
        select(func.count(WorkflowRunModel.id))
    )
    total_optimizations = total_opt.scalar() or 0

    total_resumes = await session.execute(text("SELECT COUNT(*) FROM resumes"))
    resume_count = total_resumes.scalar() or 0

    ats_scores = await session.execute(
        select(func.avg(
            func.cast(
                func.jsonb_extract_path_text(
                    WorkflowRunModel.state_data, "ats_report", "score"
                ),
                type_=__import__("sqlalchemy").Float,
            )
        )).where(WorkflowRunModel.state_data.isnot(None))
    )
    avg_ats = ats_scores.scalar() or 0.0

    total_events = await session.execute(
        select(func.count(GuardrailEventModel.id))
    )
    total_guardrail = total_events.scalar() or 0

    repaired_events = await session.execute(
        select(func.count(GuardrailEventModel.id)).where(
            GuardrailEventModel.repaired == True
        )
    )
    total_repaired = repaired_events.scalar() or 0

    if total_guardrail > 0:
        guardrail_pass_rate = round((total_guardrail - total_repaired) / total_guardrail, 4)
    else:
        guardrail_pass_rate = 1.0

    avg_improvement = round(avg_ats, 1) if avg_ats else 0.0

    return AnalyticsDashboardResponse(
        total_optimizations=total_optimizations,
        average_ats_improvement=avg_improvement,
        guardrail_pass_rate=guardrail_pass_rate,
        total_resumes=resume_count,
    )
