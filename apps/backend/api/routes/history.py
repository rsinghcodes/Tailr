import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field

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
    total_optimizations: int = 42
    average_ats_improvement: float = 24.5
    guardrail_pass_rate: float = 0.98
    total_resumes: int = 15


@router.get("/history", response_model=HistoryResponse)
async def get_optimization_history():
    """Retrieve optimization workflow history."""
    items = [
        WorkflowHistoryItem(
            workflow_id="wf-101",
            resume_title="Master Software Engineer",
            job_title="Senior AI Platform Engineer",
            status="COMPLETED",
            ats_score=88.5,
            created_at="2026-07-25T10:00:00Z",
        )
    ]
    return HistoryResponse(workflows=items, total=len(items))


@router.get("/analytics", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard():
    """Retrieve dashboard analytics and metrics."""
    return AnalyticsDashboardResponse()
