from pydantic import BaseModel, Field


class PlanOutput(BaseModel):
    target_sections: list[str] = Field(default_factory=list)
    rewrite_order: list[str] = Field(default_factory=list)
    expected_ats_delta: int = 15
    strategy: str = ""
