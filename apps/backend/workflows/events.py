from datetime import datetime, timezone
import uuid
from typing import Any
from pydantic import BaseModel, Field


class BaseWorkflowEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_version: int = 1
    workflow_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


class ResumeUploadedEvent(BaseWorkflowEvent):
    event_type: str = "resume.uploaded"


class ResumeParsedEvent(BaseWorkflowEvent):
    event_type: str = "resume.parsed"


class KnowledgeIndexedEvent(BaseWorkflowEvent):
    event_type: str = "knowledge.indexed"


class JDAnalyzedEvent(BaseWorkflowEvent):
    event_type: str = "jd.analyzed"


class PlanningCompletedEvent(BaseWorkflowEvent):
    event_type: str = "planning.completed"


class RetrievalCompletedEvent(BaseWorkflowEvent):
    event_type: str = "retrieval.completed"


class RewriteCompletedEvent(BaseWorkflowEvent):
    event_type: str = "rewrite.completed"


class GuardrailsCompletedEvent(BaseWorkflowEvent):
    event_type: str = "guardrails.completed"


class ValidationCompletedEvent(BaseWorkflowEvent):
    event_type: str = "validation.completed"


class ATSGeneratedEvent(BaseWorkflowEvent):
    event_type: str = "ats.generated"


class RenderingCompletedEvent(BaseWorkflowEvent):
    event_type: str = "rendering.completed"
