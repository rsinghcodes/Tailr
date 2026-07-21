from enum import Enum
from typing import Any
from pydantic import Field

from domain.resume.models import Resume, BaseDomainModel
from domain.job_description.models import JobDescription
from domain.evaluation.models import ValidationResult
from domain.ats.models import ATSReport


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    PARSING = "PARSING"
    INDEXING = "INDEXING"
    RETRIEVING = "RETRIEVING"
    PLANNING = "PLANNING"
    REWRITING = "REWRITING"
    VALIDATING = "VALIDATING"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowState(BaseDomainModel):
    resume: Resume | None = None
    job_description: JobDescription | None = None
    retrieved_context: list[Any] = Field(default_factory=list)
    rewrite_plan: Any | None = None
    rewritten_resume: Resume | None = None
    validation_report: ValidationResult | None = None
    ats_report: ATSReport | None = None
    status: WorkflowStatus = WorkflowStatus.PENDING
