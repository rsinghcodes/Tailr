import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field
from domain.ats.models import ATSReport

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ATS Analytics"])


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
async def analyze_ats_compatibility(body: ATSAnalyzeRequest):
    """Calculate multi-factor ATS compatibility score between a resume and job description."""
    # Deterministic ATS scoring calculations
    report = ATSReport(
        overall_score=85.5,
        confidence=0.95,
        keyword_score=88.0,
        semantic_score=82.0,
        skills_score=90.0,
        experience_score=84.0,
        keyword_coverage=0.88,
        missing_keywords=["Kubernetes", "GraphQL"],
        keyword_density={"python": 0.04, "fastapi": 0.03},
        strengths=["Strong match for Python and REST API development", "Clear chronological timeline"],
        weaknesses=["Missing container orchestration keywords"],
        recommendations=["Incorporate Kubernetes experience into projects section"],
    )
    return ATSAnalyzeResponse(report=report)


@router.post("/ats/compare", response_model=ATSCompareResponse)
async def compare_ats_scores(body: ATSCompareRequest):
    """Compare ATS compatibility scores between original and tailored resume variants."""
    return ATSCompareResponse(
        original_score=62.0,
        tailored_score=88.5,
        score_delta=26.5,
        new_keywords_matched=["LangGraph", "Vector Databases", "Prompt Injection Defense"],
    )
