from pydantic import BaseModel, Field


class RewriteOutput(BaseModel):
    summary: str | None = None
    experience: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    skills: list[dict] = Field(default_factory=list)
