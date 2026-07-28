from datetime import datetime, timezone
from typing import TypedDict, Optional, Any
from uuid import uuid4


class WorkflowState(TypedDict, total=False):
    request_id: str
    workflow_id: str
    user_id: str

    raw_resume_text: Optional[str]
    job_description_text: Optional[str]

    canonical_resume: Optional[dict[str, Any]]
    job_requirements: Optional[dict[str, Any]]
    retrieved_context: Optional[str]
    rewrite_plan: Optional[dict[str, Any]]
    rewritten_resume: Optional[dict[str, Any]]
    guardrail_report: Optional[dict[str, Any]]
    validation_report: Optional[dict[str, Any]]
    ats_report: Optional[dict[str, Any]]
    render_result: Optional[str]

    telemetry: dict[str, Any]
    errors: list[str]
