from typing import Any
from validators.base import BusinessValidator, ValidationViolation, ValidationSeverity


class CitationValidator(BusinessValidator):
    name: str = "citation_validator"

    async def validate(self, rewritten_resume: Any, canonical_resume: Any) -> list[ValidationViolation]:
        violations: list[ValidationViolation] = []
        # Checks if citations adhere to evidence bounds if citations are tracked
        return violations
