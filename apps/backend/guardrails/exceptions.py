from typing import Any
from guardrails.base import GuardrailResult, GuardrailViolation


class GuardrailError(Exception):
    """Base exception for all Guardrail failures."""

    def __init__(self, message: str, violations: list[GuardrailViolation] | None = None, metadata: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.violations = violations or []
        self.metadata = metadata or {}


class GuardrailRejectionError(GuardrailError):
    """Raised when AI content is rejected by Guardrails Engine."""

    def __init__(self, result: GuardrailResult, message: str = "AI output rejected by Guardrails Engine"):
        super().__init__(message=message, violations=result.violations, metadata=result.metadata)
        self.result = result


class SchemaValidationError(GuardrailError):
    """Raised when AI output fails structural or JSON schema validation."""

    pass


class HallucinationDetectedError(GuardrailError):
    """Raised when AI output contains fabricated facts not present in Canonical Resume Model."""

    pass


class PromptInjectionDetectedError(GuardrailError):
    """Raised when untrusted input contains prompt injection patterns."""

    pass


class LatexSafetyError(GuardrailError):
    """Raised when AI output contains illegal LaTeX commands."""

    pass


class ATSValidationError(GuardrailError):
    """Raised when AI output violates ATS formatting constraints."""

    pass


class PIILeakageError(GuardrailError):
    """Raised when AI output contains unredacted secrets or sensitive personal data."""

    pass
