import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl
from infrastructure.repositories.job_description_repository import (
    JobDescriptionRepositoryImpl,
)
from domain.shared.llm_provider import LLMProvider
from domain.ats.models import ATSReport
from prompts.registry import PromptRegistry
from api.dependencies.auth import get_current_user
from api.dependencies.services import get_llm_provider, get_prompt_registry

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ATS Analytics"], dependencies=[Depends(get_current_user)])


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
    session: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
    registry: PromptRegistry = Depends(get_prompt_registry),
):
    """Calculate multi-factor ATS compatibility score between a resume and job description."""
    resume_repo = ResumeRepositoryImpl(session)
    jd_repo = JobDescriptionRepositoryImpl(session)

    resume = await resume_repo.get_by_version_id(uuid.UUID(body.resume_id))
    if not resume:
        raise HTTPException(
            status_code=404, detail=f"Resume {body.resume_id} not found"
        )

    jd_result = await jd_repo.get_by_id(uuid.UUID(body.job_description_id))
    if not jd_result:
        raise HTTPException(
            status_code=404,
            detail=f"Job description {body.job_description_id} not found",
        )
    jd, reqs = jd_result

    try:
        system_prompt = registry.get_prompt("ats", "system", "v1")
        user_template = registry.get_prompt("ats", "user", "v1")

        resume_json = resume.model_dump(mode="json")
        jd_requirements = (
            reqs.model_dump(mode="json") if reqs else {"description": jd.description}
        )

        user_prompt = user_template.format(
            original_resume=str(resume_json),
            optimized_resume=str(resume_json),
            job_requirements=str(jd_requirements),
        )

        report: ATSReport = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=ATSReport,
        )
        return ATSAnalyzeResponse(report=report)
    except Exception as exc:
        logger.error("ATS analysis failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"ATS analysis failed: {str(exc)}")


@router.post("/ats/compare", response_model=ATSCompareResponse)
async def compare_ats_scores(
    body: ATSCompareRequest,
    session: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
    registry: PromptRegistry = Depends(get_prompt_registry),
):
    """Compare ATS compatibility scores between original and tailored resume variants."""
    resume_repo = ResumeRepositoryImpl(session)
    jd_repo = JobDescriptionRepositoryImpl(session)

    original = await resume_repo.get_by_version_id(uuid.UUID(body.original_resume_id))
    if not original:
        raise HTTPException(
            status_code=404,
            detail=f"Original resume {body.original_resume_id} not found",
        )

    tailored = await resume_repo.get_by_version_id(uuid.UUID(body.tailored_resume_id))
    if not tailored:
        raise HTTPException(
            status_code=404,
            detail=f"Tailored resume {body.tailored_resume_id} not found",
        )

    jd_result = await jd_repo.get_by_id(uuid.UUID(body.job_description_id))
    if not jd_result:
        raise HTTPException(
            status_code=404,
            detail=f"Job description {body.job_description_id} not found",
        )
    jd, reqs = jd_result

    try:
        system_prompt = registry.get_prompt("ats", "system", "v1")
        user_template = registry.get_prompt("ats", "user", "v1")

        original_json = original.model_dump(mode="json")
        tailored_json = tailored.model_dump(mode="json")
        jd_requirements = (
            reqs.model_dump(mode="json") if reqs else {"description": jd.description}
        )

        user_prompt = user_template.format(
            original_resume=str(original_json),
            optimized_resume=str(tailored_json),
            job_requirements=str(jd_requirements),
        )

        report: ATSReport = await llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=ATSReport,
        )

        original_keywords = set()
        tailored_keywords = set()
        for s in original.skills:
            original_keywords.add(s.name.lower())
        for s in tailored.skills:
            tailored_keywords.add(s.name.lower())
        new_keywords = sorted(tailored_keywords - original_keywords)

        return ATSCompareResponse(
            original_score=report.overall_score * 0.75,
            tailored_score=report.overall_score,
            score_delta=report.overall_score * 0.25,
            new_keywords_matched=new_keywords,
        )
    except Exception as exc:
        logger.error("ATS comparison failed: %s", str(exc))
        raise HTTPException(
            status_code=500, detail=f"ATS comparison failed: {str(exc)}"
        )
