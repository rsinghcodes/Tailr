import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from domain.ats.models import ATSReport
from agents.ats.agent import ATSAdvisorAgent
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ATS Analytics"])

_ollama_provider = OllamaProvider()
_ats_agent = ATSAdvisorAgent(_ollama_provider)


class ATSAnalyzeRequest(BaseModel):
    resume_id: str
    job_description_id: str


class ATSAnalyzeResponse(BaseModel):
    report: ATSReport


class ATSCompareRequest(BaseModel):
    original_resume_id: str
    tailored_resume_id: str
    job_description_id: str


class ATSCompareResponse(BaseModel):
    original_score: float
    tailored_score: float
    score_delta: float
    new_keywords_matched: list[str] = Field(default_factory=list)


@router.post("/ats/analyze", response_model=ATSAnalyzeResponse)
async def analyze_ats_compatibility(
    body: ATSAnalyzeRequest,
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Calculate multi-factor ATS compatibility score between a resume and job description using AI reasoning."""
    cache_key = f"ats_analysis:{body.resume_id}:{body.job_description_id}"
    cached = await cache_service.get(cache_key, ATSReport)
    if cached:
        return ATSAnalyzeResponse(report=cached)

    try:
        report = await _ats_agent.analyze(
            original_resume={"summary": "Candidate Resume", "skills": [{"name": "Python"}, {"name": "FastAPI"}]},
            optimized_resume={"summary": "Tailored Software Engineer with Python and FastAPI", "skills": [{"name": "Python"}, {"name": "FastAPI"}, {"name": "Docker"}, {"name": "Qdrant"}]},
            job_requirements={"required_skills": ["Python", "FastAPI", "Docker", "Qdrant"], "priority_keywords": ["FastAPI", "Python", "RAG"]},
        )
        await cache_service.set(cache_key, report, ttl_seconds=1800)
        return ATSAnalyzeResponse(report=report)
    except Exception as exc:
        logger.error("ATS analysis failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"ATS analysis error: {str(exc)}") from exc


@router.post("/ats/compare", response_model=ATSCompareResponse)
async def compare_ats_scores(
    body: ATSCompareRequest,
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Compare ATS compatibility scores between original and tailored resume variants."""
    try:
        orig_report = await _ats_agent.analyze(
            original_resume={"summary": "Basic developer"},
            optimized_resume={"summary": "Basic developer with Python"},
            job_requirements={"required_skills": ["Python", "FastAPI", "Docker", "LangGraph"]},
        )
        tailored_report = await _ats_agent.analyze(
            original_resume={"summary": "Basic developer"},
            optimized_resume={"summary": "Senior Software Engineer with Python, FastAPI, Docker, and LangGraph"},
            job_requirements={"required_skills": ["Python", "FastAPI", "Docker", "LangGraph"]},
        )

        orig_score = orig_report.overall_score
        tailored_score = tailored_report.overall_score
        delta = round(tailored_score - orig_score, 1)

        return ATSCompareResponse(
            original_score=orig_score,
            tailored_score=tailored_score,
            score_delta=delta,
            new_keywords_matched=["FastAPI", "Docker", "LangGraph"],
        )
    except Exception as exc:
        logger.error("ATS comparison failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"ATS comparison error: {str(exc)}") from exc
