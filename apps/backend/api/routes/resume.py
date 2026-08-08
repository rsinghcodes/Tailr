import logging
import uuid
from typing import Any, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from api.dependencies.auth import get_current_user
from api.dependencies.services import (
    get_resume_service,
    get_llama_extractor,
)
from api.routes.resume_schemas import (
    ResumeDetailsResponse,
    ResumeListResponse,
    ResumeListItem,
    ResumeRenderRequest,
    ResumeUploadResponse,
    ResumeVersionItem,
    ResumeVersionsResponse,
)
from application.resume.service import ResumeService
from infrastructure.llamaindex.extractors import LlamaExtractor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resumes"], dependencies=[Depends(get_current_user)])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".tex"}


@router.post("/resumes", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile,
    title: Optional[str] = Form(None),
    resume_container_id: Optional[uuid.UUID] = Form(None),
    service: ResumeService = Depends(get_resume_service),
    extractor: LlamaExtractor = Depends(get_llama_extractor),
):
    """Upload a resume file (PDF, DOCX, TXT). Extracts structured data via LlamaExtract."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    try:
        content_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to read file: {exc}"
        ) from exc

    extracted = await extractor.extract_resume(content_bytes, file.filename)

    try:
        resume, container_id = await service.upload_resume(
            extracted=extracted,
            filename=file.filename,
            title=title,
            resume_container_id=resume_container_id,
        )

        from infrastructure.llamaindex.vector_store import VectorStoreService

        vector_store = VectorStoreService()
        resume_dict = resume.model_dump(mode="json")
        await vector_store.index_structured_extraction(
            data=resume_dict,
            source_type="resume",
            source_id=str(container_id),
        )

        return ResumeUploadResponse(resume_id=container_id, status="uploaded")
    except Exception as exc:
        logger.error("Failed to upload resume: %s", str(exc))
        raise HTTPException(
            status_code=422, detail=f"Resume upload failed: {str(exc)}"
        ) from exc


@router.post("/resumes/render-pdf")
async def render_resume_pdf(payload: ResumeRenderRequest):
    """Render a resume (JSON payload, e.g. an optimized rewrite) as a downloadable PDF."""
    pdf_bytes = _render_pdf(payload.resume)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="optimized_resume.pdf"'
        },
    )


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

    pdf_bytes = _render_pdf(resume)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'
        },
    )


def _sanitize(text: Any) -> str:
    value = "" if text is None else str(text)
    value = (
        value.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2022", "-")
    )
    return value.encode("latin-1", "replace").decode("latin-1")


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _render_pdf(payload: Any) -> bytes:
    from fpdf import FPDF

    data: dict[str, Any] = {}
    if isinstance(payload, dict):
        data = payload
    else:
        dumped = getattr(payload, "model_dump", None)
        if callable(dumped):
            data = payload.model_dump(exclude_none=True)
        else:
            data = payload

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    avail = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 16)
    pdf.x = pdf.l_margin
    pdf.cell(0, 10, "Resume", ln=True, align="C")
    pdf.ln(4)

    summary = _sanitize(data.get("summary"))
    if summary:
        pdf.set_font("Helvetica", "B", 12)
        pdf.x = pdf.l_margin
        pdf.cell(0, 8, "Summary", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(avail, 6, summary)
        pdf.ln(4)

    skills = _as_list(data.get("skills"))
    if skills:
        pdf.set_font("Helvetica", "B", 12)
        pdf.x = pdf.l_margin
        pdf.cell(0, 8, "Skills", ln=True)
        pdf.set_font("Helvetica", "", 10)
        skill_names = []
        for s in skills:
            if isinstance(s, dict):
                if s.get("name"):
                    skill_names.append(_sanitize(s["name"]))
            elif isinstance(s, str) and s.strip():
                skill_names.append(_sanitize(s))
        pdf.multi_cell(avail, 6, ", ".join(skill_names))
        pdf.ln(4)

    experience = _as_list(data.get("experience"))
    if experience:
        pdf.set_font("Helvetica", "B", 12)
        pdf.x = pdf.l_margin
        pdf.cell(0, 8, "Experience", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for exp in experience:
            if not isinstance(exp, dict):
                continue
            role = _sanitize(exp.get("role"))
            company = _sanitize(exp.get("company"))
            start_date = _sanitize(exp.get("start_date"))
            end_date = _sanitize(exp.get("end_date")) or "Present"
            pdf.set_font("Helvetica", "B", 10)
            pdf.x = pdf.l_margin
            pdf.cell(0, 6, f"{role} at {company}", ln=True)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, f"{start_date} - {end_date}", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for bullet in _as_list(exp.get("bullets")):
                bullet_text = bullet.get("text") if isinstance(bullet, dict) else bullet
                pdf.multi_cell(avail, 6, f"  - {_sanitize(bullet_text)}")
            pdf.ln(2)

    projects = _as_list(data.get("projects"))
    if projects:
        pdf.set_font("Helvetica", "B", 12)
        pdf.x = pdf.l_margin
        pdf.cell(0, 8, "Projects", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for proj in projects:
            if not isinstance(proj, dict):
                continue
            title = _sanitize(proj.get("title"))
            description = _sanitize(proj.get("description"))
            pdf.set_font("Helvetica", "B", 10)
            pdf.x = pdf.l_margin
            pdf.cell(0, 6, title, ln=True)
            if description:
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(avail, 6, description)
            pdf.ln(1)

    education = _as_list(data.get("education"))
    if education:
        pdf.set_font("Helvetica", "B", 12)
        pdf.x = pdf.l_margin
        pdf.cell(0, 8, "Education", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for edu in education:
            if not isinstance(edu, dict):
                continue
            degree = _sanitize(edu.get("degree"))
            institution = _sanitize(edu.get("institution"))
            pdf.x = pdf.l_margin
            pdf.cell(0, 6, f"{degree} - {institution}", ln=True)

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
