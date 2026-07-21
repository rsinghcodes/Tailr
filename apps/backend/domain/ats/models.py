from pydantic import BaseModel, Field


class ATSReport(BaseModel):
    overall_score: float
    keyword_coverage: float
    missing_keywords: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
