import uuid
from enum import Enum
from typing import Any
from pydantic import Field

from domain.resume.models import Resume, BaseDomainModel
from domain.job_description.models import JobDescription
from domain.evaluation.models import ValidationResult
from domain.ats.models import ATSReport


class WorkflowStatus(str, Enum):
    NEW = "NEW"
    PENDING = "PENDING"  # Alias for backward compatibility
    PARSING = "PARSING"
    INDEXING = "INDEXING"
    JD_ANALYSIS = "JD_ANALYSIS"
    RETRIEVING = "RETRIEVING"
    PLANNING = "PLANNING"
    REWRITING = "REWRITING"
    GUARDRAILS = "GUARDRAILS"
    VALIDATING = "VALIDATING"
    ATS_ANALYSIS = "ATS_ANALYSIS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RENDERING = "RENDERING"
    COMPILING = "COMPILING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkflowState(BaseDomainModel):
    workflow_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    request_id: str | None = None
    resume: Resume | None = None
    job_description: JobDescription | None = None
    retrieved_context: list[Any] = Field(default_factory=list)
    rewrite_plan: Any | None = None
    rewritten_resume: Resume | None = None
    guardrail_report: Any | None = None
    validation_report: ValidationResult | None = None
    ats_report: ATSReport | None = None
    render_result: Any | None = None
    telemetry: dict[str, Any] = Field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.NEW
