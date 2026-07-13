import uuid
from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    description: str


class JobRequirements(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    experience_level: str | None = None
