from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Any
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    NEW = "NEW"
    PARSING = "PARSING"
    INDEXING = "INDEXING"
    JD_ANALYSIS = "JD_ANALYSIS"
    RESUME_ANALYSIS = "RESUME_ANALYSIS"
    RETRIEVAL = "RETRIEVAL"
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


class WorkflowTelemetry(BaseModel):
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    current_step: str = "NEW"
    step_history: list[str] = Field(default_factory=list)
    token_usage: int = 0
    latency_ms: float = 0.0
    prompt_versions: dict[str, str] = Field(default_factory=dict)
    model_versions: dict[str, str] = Field(default_factory=dict)
    trace_id: str | None = None


class WorkflowState(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    status: WorkflowStatus = WorkflowStatus.NEW

    raw_resume_text: str | None = None
    job_description_text: str | None = None

    canonical_resume: dict[str, Any] | None = None
    job_requirements: dict[str, Any] | None = None
    resume_analysis: dict[str, Any] | None = None
    retrieved_context: str | None = None
    rewrite_plan: dict[str, Any] | None = None
    rewritten_resume: dict[str, Any] | None = None
    guardrail_report: dict[str, Any] | None = None
    validation_report: dict[str, Any] | None = None
    ats_report: dict[str, Any] | None = None
    render_result: str | None = None

    telemetry: WorkflowTelemetry = Field(default_factory=WorkflowTelemetry)
    retry_count: int = 0
    errors: list[str] = Field(default_factory=list)
