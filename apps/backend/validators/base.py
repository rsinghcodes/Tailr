from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationViolation(BaseModel):
    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    field: str | None = None


class ValidationReport(BaseModel):
    status: str = "PASSED"
    checks_run: int = 0
    violations: list[ValidationViolation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BusinessValidator(ABC):
    """Abstract Base Class for all Deterministic Business Rule Validators."""

    name: str = "business_validator"

    @abstractmethod
    async def validate(self, rewritten_resume: Any, canonical_resume: Any) -> list[ValidationViolation]:
        """Validate business rules on Guardrails-approved content."""
        pass
