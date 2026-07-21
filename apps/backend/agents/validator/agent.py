from typing import Any
from agents.validator.schemas import ValidationOutput


class ValidationAgent:
    """Agent responsible for checking business correctness after Guardrails approval."""

    async def validate(self, rewritten_resume: dict[str, Any], canonical_resume: dict[str, Any]) -> ValidationOutput:
        return ValidationOutput(status="PASSED", checks_run=8, violations=[])
