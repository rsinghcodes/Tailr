import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from domain.resume.models import Resume


class ResumeUploadResponse(BaseModel):
    resume_id: uuid.UUID
    status: str = "uploaded"


class ResumeListItem(BaseModel):
    id: uuid.UUID
    title: str
    current_version: int
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ResumeListResponse(BaseModel):
    success: bool = True
    data: list[ResumeListItem]


class ResumeVersionItem(BaseModel):
    version_id: uuid.UUID
    version: int
    latex_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ResumeVersionsResponse(BaseModel):
    success: bool = True
    data: list[ResumeVersionItem]


class ResumeDetailsResponse(BaseModel):
    success: bool = True
    data: Resume


class StandardError(BaseModel):
    code: str
    message: str


class StandardErrorResponse(BaseModel):
    success: bool = False
    error: StandardError
