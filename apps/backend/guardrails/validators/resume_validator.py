import re
import time
from datetime import date, datetime
from typing import Any, Optional
from guardrails.base import (
    BaseValidator,
    GuardrailContext,
    GuardrailResult,
    GuardrailResultStatus,
    GuardrailViolation,
    ViolationSeverity,
)

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_date(value: Any) -> Optional[date]:
    """Tolerantly parse resume date strings into a date for chronological comparison."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None

    # ISO: YYYY-MM-DD or YYYY/MM/DD
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass

    # YYYY-MM or YYYY/MM
    for fmt in ("%Y-%m", "%Y/%m"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass

    # "Month YYYY" (full or abbreviated, case-insensitive)
    match = re.fullmatch(r"([A-Za-z]+)[.\s]*(\d{4})", text)
    if match:
        month_name = match.group(1).lower().rstrip(".")
        month = _MONTHS.get(month_name)
        if month:
            return date(int(match.group(2)), month, 1)

    # "MM/YYYY"
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", text)
    if match:
        return date(int(match.group(2)), int(match.group(1)), 1)

    # "YYYY"
    if re.fullmatch(r"\d{4}", text):
        return date(int(text), 1, 1)

    return None


class ResumeValidator(BaseValidator):
    name: str = "resume_validator"

    async def validate(
        self, content: Any, context: GuardrailContext
    ) -> GuardrailResult:
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
                        start_dt = _parse_date(start)
                        end_dt = _parse_date(end)
                        if (
                            start_dt is not None
                            and end_dt is not None
                            and start_dt > end_dt
                        ):
                            violations.append(
                                GuardrailViolation(
                                    code="INVALID_DATE_RANGE",
                                    message=f"Experience #{idx + 1} start date ({start}) is after end date ({end})",
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
