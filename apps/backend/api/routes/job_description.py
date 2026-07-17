import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.services import get_job_description_service
from api.routes.job_description_schemas import (
    JobDescriptionCreateRequest,
    JobDescriptionResponse,
    JobDescriptionResponseData,
)
from application.job_description.service import JobDescriptionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Job Descriptions"])


@router.post(
    "/job-descriptions", response_model=JobDescriptionResponse, status_code=201
)
async def create_job_description(
    payload: JobDescriptionCreateRequest,
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """Analyze and create a new Job Description."""
    try:
        jd, reqs = await service.create_job_description(
            title=payload.title,
            description=payload.description,
            company=payload.company,
            location=payload.location,
            employment_type=payload.employment_type,
            model=payload.model,
        )

        response_data = JobDescriptionResponseData(
            id=jd.id,
            title=jd.title,
            company=jd.company,
            location=jd.location,
            employment_type=jd.employment_type,
            description=jd.description,
            parsed_requirements=reqs,
        )
        return JobDescriptionResponse(success=True, data=response_data)
    except Exception as exc:
        logger.error("Failed to analyze job description: %s", str(exc))
        raise HTTPException(
            status_code=422, detail=f"Job description analysis failed: {str(exc)}"
        ) from exc


@router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    jd_id: uuid.UUID,
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """Retrieve a job description and its parsed requirements by ID."""
    result = await service.get_job_description(jd_id)
    if not result:
        raise HTTPException(
            status_code=404, detail="Job description not found."
        )

    jd, reqs = result
    response_data = JobDescriptionResponseData(
        id=jd.id,
        title=jd.title,
        company=jd.company,
        location=jd.location,
        employment_type=jd.employment_type,
        description=jd.description,
        parsed_requirements=reqs,
    )
    return JobDescriptionResponse(success=True, data=response_data)


@router.delete("/job-descriptions/{jd_id}", status_code=200)
async def delete_job_description(
    jd_id: uuid.UUID,
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """Delete a Job Description by ID."""
    success = await service.delete_job_description(jd_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Job description not found."
        )
    return {"success": True, "message": "Job description deleted successfully."}
