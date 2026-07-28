import logging
import os
import tempfile
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from api.dependencies.services import get_resume_service, get_llama_parser, get_llama_extractor
from api.routes.resume_schemas import (
    ResumeDetailsResponse,
    ResumeListResponse,
    ResumeListItem,
    ResumeUploadResponse,
    ResumeVersionItem,
    ResumeVersionsResponse,
)
from application.resume.service import ResumeService
from infrastructure.llamaindex.parser import LlamaDocParser
from infrastructure.llamaindex.extractors import LlamaExtractor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".tex"}


@router.post("/resumes", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile,
    title: Optional[str] = Form(None),
    resume_container_id: Optional[uuid.UUID] = Form(None),
    service: ResumeService = Depends(get_resume_service),
    parser: LlamaDocParser = Depends(get_llama_parser),
    extractor: LlamaExtractor = Depends(get_llama_extractor),
):
    """Upload a resume file (PDF, DOCX, TXT). Parses and extracts structured data via LlamaCloud."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        content_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}") from exc

    raw_text = ""
    if ext in (".pdf", ".docx"):
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(content_bytes)
                tmp_path = tmp.name
            parsed = await parser.parse_file(tmp_path)
            raw_text = parsed[0]["text"] if parsed else content_bytes.decode("utf-8", errors="replace")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
    else:
        raw_text = content_bytes.decode("utf-8")

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Parsed content is empty.")

    extracted = await extractor.extract_resume(raw_text)

    try:
        resume, container_id = await service.upload_resume(
            raw_text=raw_text,
            extracted=extracted,
            filename=file.filename,
            title=title,
            resume_container_id=resume_container_id,
        )
        return ResumeUploadResponse(resume_id=container_id, status="uploaded")
    except Exception as exc:
        logger.error("Failed to upload resume: %s", str(exc))
        raise HTTPException(
            status_code=422, detail=f"Resume upload failed: {str(exc)}"
        ) from exc


@router.get("/resumes/{resume_id}/download")
async def download_resume_pdf(
    resume_id: uuid.UUID,
    service: ResumeService = Depends(get_resume_service),
):
    """Download a resume as PDF."""
    versions = await service.get_resume_versions(resume_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Resume not found.")

    latest_version_id = versions[0]["version_id"]
    resume = await service.get_resume_by_version(latest_version_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume version not found.")

    pdf_bytes = _generate_pdf(resume)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'},
    )


def _generate_pdf(resume) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Resume", ln=True, align="C")
    pdf.ln(4)

    if resume.summary:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Summary", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, resume.summary)
        pdf.ln(4)

    if resume.skills:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Skills", ln=True)
        pdf.set_font("Helvetica", "", 10)
        skills_text = ", ".join(s.name for s in resume.skills if s.name)
        pdf.multi_cell(0, 6, skills_text)
        pdf.ln(4)

    if resume.experience:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Experience", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for exp in resume.experience:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, f"{exp.role} at {exp.company}", ln=True)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, f"{exp.start_date} - {exp.end_date or 'Present'}", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for bullet in exp.bullets:
                pdf.multi_cell(0, 6, f"  - {bullet.text}")
            pdf.ln(2)

    if resume.projects:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Projects", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for proj in resume.projects:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, proj.title, ln=True)
            if proj.description:
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, proj.description)
            pdf.ln(1)

    if resume.education:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Education", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for edu in resume.education:
            pdf.cell(0, 6, f"{edu.degree} - {edu.institution}", ln=True)

    return bytes(pdf.output())


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
