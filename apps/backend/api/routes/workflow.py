import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field

from workflows.state import WorkflowState, WorkflowStatus
from workflows.engine import WorkflowEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workflows"])
engine = WorkflowEngine()


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
async def start_workflow(request: WorkflowStartRequest):
    """Start an event-driven resume optimization workflow."""
    state = WorkflowState(
        raw_resume_text=request.raw_resume_text,
        job_description_text=request.job_description_text,
    )

    try:
        final_state = await engine.execute_workflow(state)
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
