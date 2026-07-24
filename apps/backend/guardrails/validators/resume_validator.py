import time
from typing import Any
from guardrails.base import (
    BaseValidator,
    GuardrailContext,
    GuardrailResult,
    GuardrailResultStatus,
    GuardrailViolation,
    ViolationSeverity,
)


class ResumeValidator(BaseValidator):
    name: str = "resume_validator"

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()

        if not isinstance(content, dict):
            return GuardrailResult(
                status=GuardrailResultStatus.APPROVED,
                repaired_content=content,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        violations = []

        # Validate summary presence if expected
        if "summary" in content and content["summary"] is not None:
            if len(content["summary"].strip()) == 0:
                violations.append(
                    GuardrailViolation(
                        code="EMPTY_SUMMARY",
                        message="Summary section cannot be empty whitespace",
                        severity=ViolationSeverity.MEDIUM,
                        field="summary",
                    )
                )

        # Validate date consistency in experience
        experiences = content.get("experience", [])
        if isinstance(experiences, list):
            for idx, exp in enumerate(experiences):
                if isinstance(exp, dict):
                    start = exp.get("start_date")
                    end = exp.get("end_date")
                    if start and end and end.lower() not in ["present", "current"]:
                        if start > end:
                            violations.append(
                                GuardrailViolation(
                                    code="INVALID_DATE_RANGE",
                                    message=f"Experience #{idx+1} start date ({start}) is after end date ({end})",
                                    severity=ViolationSeverity.HIGH,
                                    field=f"experience[{idx}].start_date",
                                )
                            )

        if violations:
            return GuardrailResult(
                status=GuardrailResultStatus.REJECTED,
                violations=violations,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        return GuardrailResult(
            status=GuardrailResultStatus.APPROVED,
            repaired_content=content,
            execution_time_ms=(time.perf_counter() - start_time) * 1000,
        )
