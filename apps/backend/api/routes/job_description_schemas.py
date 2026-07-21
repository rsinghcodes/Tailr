import uuid
from typing import Optional
from pydantic import BaseModel
from domain.job_description.models import JobRequirements


class JobDescriptionCreateRequest(BaseModel):
    title: str
    description: str
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    model: Optional[str] = None


class JobDescriptionResponseData(BaseModel):
    id: uuid.UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: str
    parsed_requirements: Optional[JobRequirements] = None


class JobDescriptionResponse(BaseModel):
    success: bool = True
    data: JobDescriptionResponseData
