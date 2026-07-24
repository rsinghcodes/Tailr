import re
from typing import Any
from validators.base import BusinessValidator, ValidationViolation, ValidationSeverity


class RuleValidator(BusinessValidator):
    name: str = "rule_validator"

    async def validate(self, rewritten_resume: Any, canonical_resume: Any) -> list[ValidationViolation]:
        violations: list[ValidationViolation] = []

        if not isinstance(rewritten_resume, dict):
            return violations

        # Rule 1: Summary section non-empty check
        summary = rewritten_resume.get("summary")
        if summary is not None and len(str(summary).strip()) < 10:
            violations.append(
                ValidationViolation(
                    code="BUSINESS_RULE_SHORT_SUMMARY",
                    message="Summary section must be at least 10 characters long.",
                    severity=ValidationSeverity.WARNING,
                    field="summary",
                )
            )

        # Rule 2: Date sequence sanity
        experiences = rewritten_resume.get("experience", [])
        if isinstance(experiences, list):
            for idx, exp in enumerate(experiences):
                if isinstance(exp, dict):
                    start = exp.get("start_date")
                    end = exp.get("end_date")
                    if start and end and end.lower() not in ["present", "current"]:
                        if start > end:
                            violations.append(
                                ValidationViolation(
                                    code="BUSINESS_RULE_INVALID_DATE_SEQUENCE",
                                    message=f"Start date ({start}) cannot be after end date ({end}) in experience #{idx+1}.",
                                    severity=ValidationSeverity.ERROR,
                                    field=f"experience[{idx}].start_date",
                                )
                            )

        return violations
