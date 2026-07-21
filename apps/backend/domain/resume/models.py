from datetime import datetime
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field


class SkillCategory(str, Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    AI = "AI"
    CLOUD = "Cloud"
    DATABASE = "Database"
    DEVOPS = "DevOps"
    PROGRAMMING_LANGUAGE = "Programming Language"
    FRAMEWORK = "Framework"
    TOOL = "Tool"


class BaseDomainModel(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1


class ResumeMetadata(BaseModel):
    template_name: str | None = None
    theme: str | None = None
    language: str = "en"
    additional_metadata: dict[str, Any] = Field(default_factory=dict)


class ExperienceBullet(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text: str
    metrics: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    priority: int = 0


class Experience(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    company: str
    role: str
    location: str | None = None
    employment_type: str | None = None
    start_date: str
    end_date: str | None = None
    technologies: list[str] = Field(default_factory=list)
    bullets: list[ExperienceBullet] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class Project(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    repository: str | None = None
    demo: str | None = None
    bullets: list[str] = Field(default_factory=list)
    category: str | None = None


class Skill(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    category: SkillCategory | str | None = None
    years: float | None = None
    proficiency: str | None = None
    verified: bool = False


class Education(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    institution: str
    degree: str
    field: str | None = None
    cgpa: float | str | None = None
    start_date: str
    end_date: str | None = None


class Achievement(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    description: str | None = None
    category: str | None = None
    date: str | None = None


class Certification(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    issuer: str
    credential_id: str | None = None
    issue_date: str | None = None


class Resume(BaseDomainModel):
    summary: str | None = None
    skills: list[Skill] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    metadata: ResumeMetadata = Field(default_factory=ResumeMetadata)
