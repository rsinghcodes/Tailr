from pydantic import BaseModel, Field


class ATSOutput(BaseModel):
    score: int = 85
    keyword_coverage: float = 0.90
    semantic_similarity: float = 0.88
    recommendations: list[str] = Field(default_factory=list)
