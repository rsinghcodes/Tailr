import logging
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from api.dependencies.auth import get_current_user
from api.dependencies.services import (
    get_job_description_service,
    get_llama_extractor,
)
from api.routes.job_description_schemas import (
    JobDescriptionCreateRequest,
    JobDescriptionListResponse,
    JobDescriptionListItem,
    JobDescriptionResponse,
    JobDescriptionResponseData,
)
from application.job_description.service import JobDescriptionService
from infrastructure.llamaindex.extractors import LlamaExtractor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Job Descriptions"], dependencies=[Depends(get_current_user)])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post(
    "/job-descriptions", response_model=JobDescriptionResponse, status_code=201
)
async def create_job_description(
    payload: JobDescriptionCreateRequest,
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """Analyze and create a new Job Description from text input."""
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


@router.post(
    "/job-descriptions/upload", response_model=JobDescriptionResponse, status_code=201
)
async def upload_job_description(
    file: UploadFile,
    title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    service: JobDescriptionService = Depends(get_job_description_service),
    extractor: LlamaExtractor = Depends(get_llama_extractor),
):
    """Upload a job description file (PDF, DOCX, TXT). Extracts structured data via LlamaExtract, then analyzes via LLM."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    try:
        content_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to read file: {exc}"
        ) from exc

    jd_title = title or file.filename
    jd_company = company

    extracted = await extractor.extract_job_requirements(content_bytes, file.filename)
    if not jd_title and extracted.title:
        jd_title = extracted.title
    if not jd_company and extracted.company:
        jd_company = extracted.company

    try:
        jd, reqs = await service.create_job_description(
            title=jd_title,
            description="",
            company=jd_company,
            location=location,
            employment_type=employment_type,
            extracted_requirements=extracted,
        )

        from infrastructure.llamaindex.vector_store import VectorStoreService

        vector_store = VectorStoreService()
        jd_dict = extracted.model_dump(mode="json")
        await vector_store.index_structured_extraction(
            data=jd_dict,
            source_type="jd",
            source_id=str(jd.id),
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
        logger.error("Failed to upload job description: %s", str(exc))
        raise HTTPException(
            status_code=422, detail=f"Job description upload failed: {str(exc)}"
        ) from exc


@router.get("/job-descriptions", response_model=JobDescriptionListResponse)
async def list_job_descriptions(
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """List all job descriptions."""
    jds = await service.list_job_descriptions()
    data = [JobDescriptionListItem(**jd) for jd in jds]
    return JobDescriptionListResponse(success=True, data=data)


@router.get("/job-descriptions/{jd_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    jd_id: uuid.UUID,
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """Retrieve a job description and its parsed requirements by ID."""
    result = await service.get_job_description(jd_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job description not found.")

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
        raise HTTPException(status_code=404, detail="Job description not found.")
    return {"success": True, "message": "Job description deleted successfully."}
