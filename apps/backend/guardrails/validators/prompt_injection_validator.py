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


class PromptInjectionValidator(BaseValidator):
    name: str = "prompt_injection_validator"

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"disregard\s+system\s+prompt",
        r"reveal\s+(system\s+)?prompt",
        r"output\s+internal\s+configuration",
        r"execute\s+this\s+command",
        r"you\s+are\s+now\s+DAN",
        r"jailbreak",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"\[SYSTEM_PROMPT\]",
        r"bypass\s+guardrails",
    ]

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()
        text = str(content)

        violations = []
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(
                    GuardrailViolation(
                        code="PROMPT_INJECTION_DETECTED",
                        message=f"Prompt injection pattern detected: '{pattern}'",
                        severity=ViolationSeverity.CRITICAL,
                        metadata={"pattern": pattern},
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
