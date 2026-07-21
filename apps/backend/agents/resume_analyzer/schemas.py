from pydantic import BaseModel, Field


class ResumeAnalysisOutput(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    candidate_level: str = "Mid"
    alignment_score: float = 0.8
