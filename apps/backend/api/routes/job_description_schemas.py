import uuid
from typing import Any, Optional
from pydantic import BaseModel


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
    raw_extracted: Optional[dict[str, Any]] = None


class JobDescriptionResponse(BaseModel):
    success: bool = True
    data: JobDescriptionResponseData


class JobDescriptionListItem(BaseModel):
    id: uuid.UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: str
    created_at: str = ""
    updated_at: str = ""


class JobDescriptionListResponse(BaseModel):
    success: bool = True
    data: list[JobDescriptionListItem]
