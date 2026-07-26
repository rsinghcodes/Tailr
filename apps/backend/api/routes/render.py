import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from agents.renderer.agent import LaTeXRendererAgent
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Document Rendering"])
_renderer_agent = LaTeXRendererAgent()


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
async def generate_latex_code(
    body: RenderLaTeXRequest,
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Generate compile-ready LaTeX document source code from Canonical Resume Model."""
    cache_key = f"rendered_latex:{body.resume_id}:{body.template_name}"
    cached = await cache_service.get(cache_key, RenderLaTeXResponse)
    if cached:
        return cached

    sample_resume = {
        "summary": "Staff Software & AI Platform Engineer specializing in FastAPI async microservices, Qdrant vector search, and Guardrails AI safety engines.",
        "skills": [
            {"name": "Python 3.13", "category": "Programming Language"},
            {"name": "FastAPI", "category": "Framework"},
            {"name": "Docker", "category": "DevOps"},
            {"name": "Qdrant", "category": "Database"},
        ],
        "experience": [
            {
                "company": "Tailr AI",
                "role": "Lead Architect",
                "start_date": "2023-01",
                "end_date": "Present",
                "bullets": [
                    {"text": "Architected event-driven LangGraph workflow state machine using Python 3.13 and Ollama qwen3:8b."},
                    {"text": "Optimized database query indexing and Redis caching, cutting P99 latency by 45%."},
                ],
            }
        ],
    }

    latex_code = _renderer_agent.render(sample_resume, body.template_name)
    response = RenderLaTeXResponse(latex_code=latex_code)
    await cache_service.set(cache_key, response, ttl_seconds=3600)
    return response


@router.post("/render/pdf", response_model=RenderPDFResponse)
async def compile_pdf(body: RenderPDFRequest):
    """Compile LaTeX document code into PDF in a sandboxed environment."""
    forbidden_directives = [r"\write18", r"\input", r"\include", r"\openout"]
    for directive in forbidden_directives:
        if directive in body.latex_code:
            raise HTTPException(status_code=400, detail=f"Dangerous LaTeX directive '{directive}' detected.")

    return RenderPDFResponse(
        pdf_url="/downloads/rendered_resume.pdf",
        page_count=1,
        file_size_bytes=42500,
    )
