from typing import Any
from validators.base import ValidationReport, ValidationViolation


class BusinessValidationError(Exception):
    """Raised when Guardrail-approved AI output fails business rule correctness checks."""

    def __init__(self, report: ValidationReport, message: str = "AI output failed business validation rules"):
        super().__init__(message)
        self.report = report
        self.message = message
        self.violations: list[ValidationViolation] = report.violations
