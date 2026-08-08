import json
import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api.dependencies.auth import get_current_user
from application.workflow.service import WorkflowApplicationService
from application.resume.service import ResumeService
from application.job_description.service import JobDescriptionService
from api.dependencies.services import (
    get_workflow_service,
    get_resume_service,
    get_job_description_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workflows"], dependencies=[Depends(get_current_user)])


class WorkflowStartRequest(BaseModel):
    resume_id: str | None = None
    job_description_id: str | None = None


class FeedbackItem(BaseModel):
    company: str | None = None
    role: str | None = None
    bullet: str = ""
    comment: str = ""


class RefineRequest(BaseModel):
    resume: dict[str, Any]
    job_description_id: str | None = None
    feedback: list[FeedbackItem] = Field(default_factory=list)
    global_comment: str | None = None


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    telemetry: dict[str, Any] = Field(default_factory=dict)
    guardrail_report: dict[str, Any] | None = None
    ats_report: dict[str, Any] | None = None
    rewritten_resume: dict[str, Any] | None = None


async def _resolve_job_requirements(
    job_description_id: str | None,
    jd_service: JobDescriptionService,
) -> dict[str, Any] | None:
    if not job_description_id:
        return None

    jd_result = await jd_service.get_job_description(uuid.UUID(job_description_id))
    if not jd_result:
        return None

    jd, _ = jd_result
    raw = jd.raw_extracted or {}
    return {
        "title": raw.get("title") or jd.title or "",
        "required_skills": raw.get("required_skills", []),
        "preferred_skills": raw.get("preferred_skills", []),
        "responsibilities": raw.get("responsibilities", []),
        "soft_skills": [],
        "keywords": raw.get("keywords", []),
        "experience_level": raw.get("seniority", ""),
    }


async def _resolve_workflow_data(
    request: WorkflowStartRequest,
    resume_service: ResumeService,
    jd_service: JobDescriptionService,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    canonical_resume = None
    job_requirements = None

    if request.resume_id:
        versions = await resume_service.get_resume_versions(
            uuid.UUID(request.resume_id)
        )
        if versions:
            resume = await resume_service.get_resume_by_version(
                versions[0]["version_id"]
            )
            if resume:
                canonical_resume = {
                    "summary": resume.summary,
                    "skills": [
                        {
                            "name": s.name,
                            "category": s.category.value if s.category else None,
                        }
                        for s in (resume.skills or [])
                    ],
                    "experience": [
                        {
                            "company": e.company,
                            "role": e.role,
                            "start_date": e.start_date,
                            "end_date": e.end_date,
                            "bullets": [{"text": b.text} for b in (e.bullets or [])],
                        }
                        for e in (resume.experience or [])
                    ],
                    "projects": [
                        {
                            "title": p.title,
                            "description": p.description,
                            "technologies": p.technologies or [],
                        }
                        for p in (resume.projects or [])
                    ],
                    "education": [
                        {
                            "institution": e.institution,
                            "degree": e.degree,
                            "start_date": e.start_date,
                            "end_date": e.end_date,
                        }
                        for e in (resume.education or [])
                    ],
                }

    job_requirements = await _resolve_job_requirements(
        request.job_description_id, jd_service
    )

    return canonical_resume, job_requirements


@router.post("/workflows/stream")
async def stream_workflow(
    request: WorkflowStartRequest,
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service),
    resume_service: ResumeService = Depends(get_resume_service),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
):
    """Stream resume optimization workflow progress via SSE.

    Events emitted:
      - workflow_start  {workflow_id, total_steps}
      - step_start      {step, step_index, total_steps, label, description}
      - step_complete   {step, step_index, total_steps, label, output}
      - workflow_complete {workflow_id, status, rewritten_resume, bullet_diff,
                           ats_report, guardrail_report, validation_report,
                           rewrite_plan, telemetry}

    bullet_diff is a diff of only the changed content (summary + per-experience
    bullets) between the original and optimized resume: {summary, experience[]}.
    """
    (
        canonical_resume,
        job_requirements,
    ) = await _resolve_workflow_data(request, resume_service, jd_service)

    async def event_generator():
        try:
            async for event in workflow_service.start_workflow_stream(
                canonical_resume=canonical_resume,
                job_requirements=job_requirements,
            ):
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
        except Exception as exc:
            logger.error("Workflow stream error: %s", str(exc))
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
        finally:
            yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/workflows/refine")
async def refine_workflow(
    request: RefineRequest,
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
):
    """Re-optimize a resume based on user feedback, streamed via SSE.

    The `resume` field is the previous optimized resume; the full 7-step
    pipeline re-runs with `user_feedback` injected into the rewrite step.

    Events emitted match `/workflows/stream`; `workflow_complete` carries
    `bullet_diff` comparing the previous optimized resume against the new one.
    """
    job_requirements = await _resolve_job_requirements(
        request.job_description_id, jd_service
    )
    user_feedback = {
        "items": [
            f.model_dump(exclude_none=True) for f in request.feedback if f.comment.strip()
        ],
        "global_comment": request.global_comment,
    }

    async def event_generator():
        try:
            async for event in workflow_service.start_workflow_stream(
                canonical_resume=request.resume,
                job_requirements=job_requirements,
                user_feedback=user_feedback,
            ):
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
        except Exception as exc:
            logger.error("Workflow refine stream error: %s", str(exc))
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"
        finally:
            yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def start_workflow(
    request: WorkflowStartRequest,
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service),
    resume_service: ResumeService = Depends(get_resume_service),
    jd_service: JobDescriptionService = Depends(get_job_description_service),
):
    """Start an event-driven resume optimization workflow."""
    try:
        (
            canonical_resume,
            job_requirements,
        ) = await _resolve_workflow_data(request, resume_service, jd_service)

        final_state = await workflow_service.start_workflow(
            canonical_resume=canonical_resume,
            job_requirements=job_requirements,
        )

        return WorkflowResponse(
            workflow_id=final_state.get("workflow_id", ""),
            status="completed",
            telemetry=final_state.get("telemetry", {}),
            guardrail_report=final_state.get("guardrail_report"),
            ats_report=final_state.get("ats_report"),
            rewritten_resume=final_state.get("rewritten_resume"),
        )
    except Exception as exc:
        logger.error("Workflow execution failed: %s", str(exc))
        raise HTTPException(
            status_code=422, detail=f"Workflow failed: {str(exc)}"
        ) from exc


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(
    workflow_id: str,
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service),
):
    """Retrieve the current state and telemetry of a specific workflow run."""
    state = await workflow_service.get_workflow_state(workflow_id)
    if not state:
        raise HTTPException(
            status_code=404, detail=f"Workflow '{workflow_id}' not found."
        )

    return WorkflowResponse(
        workflow_id=state.get("workflow_id", workflow_id),
        status=state.get("status", "unknown"),
        telemetry=state.get("telemetry", {}),
        guardrail_report=state.get("guardrail_report"),
        ats_report=state.get("ats_report"),
        rewritten_resume=state.get("rewritten_resume"),
    )
