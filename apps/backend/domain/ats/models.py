from pydantic import BaseModel, Field


class ATSReport(BaseModel):
    overall_score: float
    confidence: float = 0.95
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    skills_score: float = 0.0
    experience_score: float = 0.0
    keyword_coverage: float = 0.0
    missing_keywords: list[str] = Field(default_factory=list)
    keyword_density: dict[str, float] = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
