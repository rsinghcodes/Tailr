import logging
from typing import Any
from validators.base import (
    BusinessValidator,
    ValidationReport,
    ValidationViolation,
    ValidationSeverity,
)
from validators.rule_validator import RuleValidator
from validators.citation_validator import CitationValidator
from validators.exceptions import BusinessValidationError

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Deterministic Business Validation Engine executing business correctness rules post-Guardrails."""

    def __init__(self, validators: list[BusinessValidator] | None = None):
        self.validators = validators or [RuleValidator(), CitationValidator()]

    async def validate(self, rewritten_resume: Any, canonical_resume: Any) -> ValidationReport:
        logger.info("Executing Business Validation Engine")
        all_violations: list[ValidationViolation] = []
        checks_run = 0

        for validator in self.validators:
            checks_run += 1
            violations = await validator.validate(rewritten_resume, canonical_resume)
            all_violations.extend(violations)

        critical_or_errors = [v for v in all_violations if v.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)]
        status = "FAILED" if critical_or_errors else "PASSED"

        report = ValidationReport(
            status=status,
            checks_run=checks_run,
            violations=all_violations,
            warnings=[v.message for v in all_violations if v.severity == ValidationSeverity.WARNING],
        )

        if status == "FAILED":
            logger.warning("Business Validation Engine failed with %d errors", len(critical_or_errors))
            raise BusinessValidationError(report)

        return report
