import json
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


class JSONValidator(BaseValidator):
    name: str = "json_validator"

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()

        if isinstance(content, (dict, list)):
            return GuardrailResult(
                status=GuardrailResultStatus.APPROVED,
                repaired_content=content,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        if not isinstance(content, str):
            return GuardrailResult(
                status=GuardrailResultStatus.REJECTED,
                violations=[
                    GuardrailViolation(
                        code="JSON_INVALID_TYPE",
                        message=f"Expected string or dict input, got {type(content).__name__}",
                        severity=ViolationSeverity.CRITICAL,
                    )
                ],
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        text = content.strip()

        # Direct JSON parse attempt
        try:
            parsed = json.loads(text)
            return GuardrailResult(
                status=GuardrailResultStatus.APPROVED,
                repaired_content=parsed,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )
        except json.JSONDecodeError:
            pass

        # Attempt Repair: strip markdown code blocks
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned_text)
            return GuardrailResult(
                status=GuardrailResultStatus.REPAIRED,
                repaired=True,
                repaired_content=parsed,
                warnings=["Stripped markdown code fences from JSON output"],
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )
        except json.JSONDecodeError:
            pass

        # Attempt Repair: fix trailing commas
        repaired_text = re.sub(r",\s*([\]}])", r"\1", cleaned_text)
        try:
            parsed = json.loads(repaired_text)
            return GuardrailResult(
                status=GuardrailResultStatus.REPAIRED,
                repaired=True,
                repaired_content=parsed,
                warnings=["Repaired trailing commas in JSON output"],
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )
        except json.JSONDecodeError as err:
            return GuardrailResult(
                status=GuardrailResultStatus.REJECTED,
                violations=[
                    GuardrailViolation(
                        code="JSON_PARSE_ERROR",
                        message=f"Malformed JSON: {err.msg} at line {err.lineno} col {err.colno}",
                        severity=ViolationSeverity.CRITICAL,
                    )
                ],
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )
