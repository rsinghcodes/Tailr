import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from domain.ats.models import ATSReport
from agents.ats.agent import ATSAdvisorAgent
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service
from infrastructure.database import get_db
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.repositories.job_description_repository import JobDescriptionRepositoryImpl

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


async def _fetch_resume_dict(resume_id: str, session: AsyncSession) -> dict:
    """Fetch a resume from DB and convert to dict for ATS agent."""
    try:
        repo = ResumeRepositoryImpl(session)
        resume = await repo.get_by_version_id(uuid.UUID(resume_id))
        if resume:
            data = resume.model_dump(mode="json")
            # Flatten skills for ATS agent
            skills_list = [{"name": s.get("name", "")} for s in data.get("skills", [])]
            return {
                "summary": data.get("summary", ""),
                "skills": skills_list,
                "experience": data.get("experience", []),
            }
    except Exception as exc:
        logger.warning("Failed to fetch resume %s: %s", resume_id, str(exc))
    return {"summary": "Candidate Resume", "skills": [], "experience": []}


async def _fetch_jd_requirements(jd_id: str, session: AsyncSession) -> dict:
    """Fetch JD requirements from DB."""
    try:
        repo = JobDescriptionRepositoryImpl(session)
        result = await repo.get_by_id(uuid.UUID(jd_id))
        if result:
            jd, reqs = result
            if reqs:
                return {
                    "required_skills": reqs.required_skills,
                    "preferred_skills": reqs.preferred_skills,
                    "keywords": reqs.keywords,
                    "priority_keywords": reqs.keywords or reqs.required_skills,
                }
            return {"required_skills": [], "priority_keywords": [], "keywords": []}
    except Exception as exc:
        logger.warning("Failed to fetch JD %s: %s", jd_id, str(exc))
    return {"required_skills": [], "priority_keywords": [], "keywords": []}


@router.post("/ats/analyze", response_model=ATSAnalyzeResponse)
async def analyze_ats_compatibility(
    body: ATSAnalyzeRequest,
    session: AsyncSession = Depends(get_db),
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Calculate multi-factor ATS compatibility score between a resume and job description."""
    cache_key = f"ats_analysis:{body.resume_id}:{body.job_description_id}"
    cached = await cache_service.get(cache_key, ATSReport)
    if cached:
        return ATSAnalyzeResponse(report=cached)

    try:
        resume_data = await _fetch_resume_dict(body.resume_id, session)
        jd_reqs = await _fetch_jd_requirements(body.job_description_id, session)

        report = await _ats_agent.analyze(
            original_resume=resume_data,
            optimized_resume=resume_data,
            job_requirements=jd_reqs,
        )
        await cache_service.set(cache_key, report, ttl_seconds=1800)
        return ATSAnalyzeResponse(report=report)
    except Exception as exc:
        logger.error("ATS analysis failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"ATS analysis error: {str(exc)}") from exc


@router.post("/ats/compare", response_model=ATSCompareResponse)
async def compare_ats_scores(
    body: ATSCompareRequest,
    session: AsyncSession = Depends(get_db),
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Compare ATS compatibility scores between original and tailored resume variants."""
    try:
        orig_data = await _fetch_resume_dict(body.original_resume_id, session)
        tailored_data = await _fetch_resume_dict(body.tailored_resume_id, session)
        jd_reqs = await _fetch_jd_requirements(body.job_description_id, session)

        orig_report = await _ats_agent.analyze(
            original_resume=orig_data,
            optimized_resume=orig_data,
            job_requirements=jd_reqs,
        )
        tailored_report = await _ats_agent.analyze(
            original_resume=orig_data,
            optimized_resume=tailored_data,
            job_requirements=jd_reqs,
        )

        orig_score = orig_report.overall_score
        tailored_score = tailored_report.overall_score
        delta = round(tailored_score - orig_score, 1)

        # Find new keywords matched
        orig_kw = set(kw.lower() for kw in orig_report.keyword_density.keys()) if orig_report.keyword_density else set()
        tailored_kw = set(kw.lower() for kw in tailored_report.keyword_density.keys()) if tailored_report.keyword_density else set()
        new_keywords = list(tailored_kw - orig_kw)[:10]

        return ATSCompareResponse(
            original_score=orig_score,
            tailored_score=tailored_score,
            score_delta=delta,
            new_keywords_matched=new_keywords,
        )
    except Exception as exc:
        logger.error("ATS comparison failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"ATS comparison error: {str(exc)}") from exc
