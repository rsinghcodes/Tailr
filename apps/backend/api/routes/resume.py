import logging
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from api.dependencies.services import get_resume_service
from api.routes.resume_schemas import (
    ResumeDetailsResponse,
    ResumeListResponse,
    ResumeListItem,
    ResumeUploadResponse,
    ResumeVersionItem,
    ResumeVersionsResponse,
)
from application.resume.service import ResumeService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resumes"])


@router.post("/resumes", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile,
    title: Optional[str] = Form(None),
    resume_container_id: Optional[uuid.UUID] = Form(None),
    service: ResumeService = Depends(get_resume_service),
):
    """Upload and parse a LaTeX resume into a canonical representation."""
    if not file.filename or not file.filename.endswith((".tex", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only LaTeX (.tex) or text (.txt) files are supported.",
        )

    try:
        content_bytes = await file.read()
        raw_latex = content_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400, detail="Invalid file encoding. File must be UTF-8 encoded."
        ) from exc

    try:
        resume = await service.upload_resume(
            raw_latex=raw_latex,
            filename=file.filename,
            title=title,
            resume_container_id=resume_container_id,
        )
        return ResumeUploadResponse(resume_id=resume.id, status="uploaded")
    except Exception as exc:
        logger.error("Failed to parse and upload resume: %s", str(exc))
        raise HTTPException(
            status_code=422, detail=f"Resume parsing failed: {str(exc)}"
        ) from exc


@router.get("/resumes", response_model=ResumeListResponse)
async def list_resumes(service: ResumeService = Depends(get_resume_service)):
    """List all parent resume containers."""
    resumes = await service.list_resumes()
    data = [ResumeListItem(**r) for r in resumes]
    return ResumeListResponse(success=True, data=data)


@router.get("/resumes/{resume_id}", response_model=ResumeDetailsResponse)
async def get_latest_resume(
    resume_id: uuid.UUID, service: ResumeService = Depends(get_resume_service)
):
    """Retrieve the details of the latest version of a specific resume container."""
    versions = await service.get_resume_versions(resume_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Resume container not found.")

    latest_version_id = versions[0]["version_id"]
    resume = await service.get_resume_by_version(latest_version_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found.")
    return ResumeDetailsResponse(success=True, data=resume)


@router.get("/resumes/{resume_id}/versions", response_model=ResumeVersionsResponse)
async def get_resume_versions(
    resume_id: uuid.UUID, service: ResumeService = Depends(get_resume_service)
):
    """List all version records for a specific resume container."""
    versions = await service.get_resume_versions(resume_id)
    data = [ResumeVersionItem(**v) for v in versions]
    return ResumeVersionsResponse(success=True, data=data)


@router.get("/resumes/versions/{version_id}", response_model=ResumeDetailsResponse)
async def get_resume_version_details(
    version_id: uuid.UUID, service: ResumeService = Depends(get_resume_service)
):
    """Retrieve details of a specific resume version by its version ID."""
    resume = await service.get_resume_by_version(version_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found.")
    return ResumeDetailsResponse(success=True, data=resume)


@router.delete("/resumes/{resume_id}", status_code=200)
async def delete_resume(
    resume_id: uuid.UUID, service: ResumeService = Depends(get_resume_service)
):
    """Delete a parent resume container and all associated version records."""
    success = await service.delete_resume_container(resume_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume container not found.")
    return {"success": True, "message": "Resume deleted successfully."}
