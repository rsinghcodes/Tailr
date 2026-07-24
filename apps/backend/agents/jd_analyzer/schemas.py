from pydantic import BaseModel, Field


class JDAnalysisOutput(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    seniority: str = "Mid"
    domain: str = "Software Engineering"
    priority_keywords: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
