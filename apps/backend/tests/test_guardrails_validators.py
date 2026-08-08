import pytest

from guardrails.validators.resume_validator import ResumeValidator, _parse_date
from guardrails.base import (
    GuardrailContext,
    ViolationSeverity,
)


def test_parse_date_variants():
    assert _parse_date("2021-01-01").isoformat() == "2021-01-01"
    assert _parse_date("2021/06/15").isoformat() == "2021-06-15"
    assert _parse_date("2021-03").isoformat() == "2021-03-01"
    assert _parse_date("May 2019").isoformat() == "2019-05-01"
    assert _parse_date("may 2019").isoformat() == "2019-05-01"
    assert _parse_date("Jul. 2019").isoformat() == "2019-07-01"
    assert _parse_date("2012").isoformat() == "2012-01-01"
    assert _parse_date("06/2019").isoformat() == "2019-06-01"
    assert _parse_date(None) is None
    assert _parse_date("") is None
    assert _parse_date("not a date") is None


async def _validate(content: dict) -> dict:
    validator = ResumeValidator()
    result = await validator.validate(content, GuardrailContext())
    return {
        "status": result.status.value,
        "codes": [v.code for v in result.violations],
        "severities": [v.severity for v in result.violations],
    }


@pytest.mark.asyncio
async def test_valid_month_year_dates_are_not_rejected():
    content = {
        "summary": "Test",
        "experience": [
            {
                "company": "Acme",
                "role": "Engineer",
                "start_date": "May 2019",
                "end_date": "July 2019",
            }
        ],
    }
    result = await _validate(content)
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_reversed_iso_dates_are_rejected():
    content = {
        "summary": "Test",
        "experience": [
            {
                "company": "Acme",
                "role": "Engineer",
                "start_date": "2021-01-01",
                "end_date": "2020-12-31",
            }
        ],
    }
    result = await _validate(content)
    assert result["status"] == "rejected"
    assert "INVALID_DATE_RANGE" in result["codes"]
    assert ViolationSeverity.HIGH in result["severities"]


@pytest.mark.asyncio
async def test_present_end_date_is_skipped():
    content = {
        "summary": "Test",
        "experience": [
            {
                "company": "Acme",
                "role": "Engineer",
                "start_date": "Jan 2020",
                "end_date": "Present",
            }
        ],
    }
    result = await _validate(content)
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_year_only_dates_are_compared():
    content = {
        "summary": "Test",
        "experience": [
            {
                "company": "Acme",
                "role": "Engineer",
                "start_date": "2016",
                "end_date": "2012",
            }
        ],
    }
    result = await _validate(content)
    assert result["status"] == "rejected"
