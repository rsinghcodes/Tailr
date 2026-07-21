import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from application.workflow.service import WorkflowApplicationService
from api.dependencies.services import get_workflow_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workflows"])


class WorkflowStartRequest(BaseModel):
    raw_resume_text: str | None = None
    job_description_text: str | None = None


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    telemetry: dict[str, Any] = Field(default_factory=dict)
    guardrail_report: dict[str, Any] | None = None
    ats_report: dict[str, Any] | None = None
    rewritten_resume: dict[str, Any] | None = None


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def start_workflow(
    request: WorkflowStartRequest,
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service),
):
    """Start an event-driven resume optimization workflow."""
    try:
        final_state = await workflow_service.start_workflow(
            raw_resume_text=request.raw_resume_text,
            job_description_text=request.job_description_text,
        )
        return WorkflowResponse(
            workflow_id=final_state.workflow_id,
            status=final_state.status.value,
            telemetry=final_state.telemetry.model_dump(),
            guardrail_report=final_state.guardrail_report,
            ats_report=final_state.ats_report,
            rewritten_resume=final_state.rewritten_resume,
        )
    except Exception as exc:
        logger.error("Workflow execution failed: %s", str(exc))
        raise HTTPException(status_code=422, detail=f"Workflow failed: {str(exc)}") from exc
