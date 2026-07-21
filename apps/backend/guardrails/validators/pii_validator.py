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


class PIIValidator(BaseValidator):
    name: str = "pii_validator"

    PII_PATTERNS = [
        (r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "JWT Token"),
        (r"(?:sk-[a-zA-Z0-9]{32,})", "OpenAI API Key"),
        (r"(?:AKIA[0-9A-Z]{16})", "AWS Access Key ID"),
        (r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "Exposed Password"),
    ]

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()
        text = str(content)

        violations = []
        for pattern, label in self.PII_PATTERNS:
            if re.search(pattern, text):
                violations.append(
                    GuardrailViolation(
                        code="PII_SECRET_LEAKAGE",
                        message=f"Detected leaked credential or sensitive token: {label}",
                        severity=ViolationSeverity.CRITICAL,
                        metadata={"type": label},
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
