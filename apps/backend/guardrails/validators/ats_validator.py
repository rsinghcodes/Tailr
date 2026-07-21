import re
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


class ATSValidator(BaseValidator):
    name: str = "ats_validator"

    FORBIDDEN_CHARACTERS = [r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"]  # Control characters

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()
        text = str(content)

        violations = []
        for pattern in self.FORBIDDEN_CHARACTERS:
            if re.search(pattern, text):
                violations.append(
                    GuardrailViolation(
                        code="ATS_UNPARSABLE_CHARACTER",
                        message="Content contains non-standard control characters that break ATS parsing",
                        severity=ViolationSeverity.HIGH,
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
