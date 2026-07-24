from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
import time
from pydantic import BaseModel, Field


class GuardrailResultStatus(str, Enum):
    APPROVED = "approved"
    REPAIRED = "repaired"
    REJECTED = "rejected"


class ViolationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GuardrailViolation(BaseModel):
    code: str
    message: str
    severity: ViolationSeverity = ViolationSeverity.HIGH
    field: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GuardrailContext(BaseModel):
    workflow_id: str | None = None
    profile_name: str = "rewrite_strict"
    canonical_resume: Any = None
    job_description: Any = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GuardrailResult(BaseModel):
    status: GuardrailResultStatus
    repaired: bool = False
    violations: list[GuardrailViolation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    repaired_content: Any = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseValidator(ABC):
    """Abstract Base Class for all Guardrail Validators."""

    name: str = "base_validator"

    @abstractmethod
    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        """Validate AI-generated content against safety and integrity rules."""
        pass
