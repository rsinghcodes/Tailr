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


class LatexSafetyValidator(BaseValidator):
    name: str = "latex_safety_validator"

    DANGEROUS_LATEX_COMMANDS = [
        r"\\input",
        r"\\include",
        r"\\write18",
        r"\\openout",
        r"\\catcode",
        r"\\immediate",
        r"\\sys",
        r"\\exec",
        r"\\read",
        r"\\openin",
    ]

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()
        text = str(content)

        # Rejection check for dangerous commands
        violations = []
        for cmd in self.DANGEROUS_LATEX_COMMANDS:
            if re.search(cmd, text):
                violations.append(
                    GuardrailViolation(
                        code="LATEX_DANGEROUS_COMMAND",
                        message=f"Illegal LaTeX command detected: '{cmd}'",
                        severity=ViolationSeverity.CRITICAL,
                        metadata={"command": cmd},
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
