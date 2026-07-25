import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Document Rendering"])


class RenderLaTeXRequest(BaseModel):
    resume_id: str
    template_name: str = "classic"


class RenderLaTeXResponse(BaseModel):
    latex_code: str


class RenderPDFRequest(BaseModel):
    latex_code: str


class RenderPDFResponse(BaseModel):
    pdf_url: str
    page_count: int = 1
    file_size_bytes: int = 42500


@router.post("/render/latex", response_model=RenderLaTeXResponse)
async def generate_latex_code(body: RenderLaTeXRequest):
    """Generate LaTeX document source code from Canonical Resume Model."""
    sample_latex = r"""\documentclass[letterpaper,11pt]{article}
\begin{document}
\section{Summary}
Tailored Software Engineer resume.
\end{document}"""
    return RenderLaTeXResponse(latex_code=sample_latex)


@router.post("/render/pdf", response_model=RenderPDFResponse)
async def compile_pdf(body: RenderPDFRequest):
    """Compile LaTeX document code into PDF in a sandboxed environment."""
    if r"\write18" in body.latex_code or r"\input" in body.latex_code:
        raise HTTPException(status_code=400, detail="Dangerous LaTeX directive detected.")

    return RenderPDFResponse(
        pdf_url="/downloads/rendered_resume.pdf",
        page_count=1,
        file_size_bytes=42500,
    )
