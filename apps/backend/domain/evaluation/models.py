from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationIssue(BaseModel):
    type: str
    severity: Severity | str
    message: str
    section: str | None = None
    recommendation: str | None = None


class ValidationResult(BaseModel):
    passed: bool
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
    hallucination_score: float = 0.0
