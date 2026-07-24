import pytest
from validators.engine import ValidationEngine
from validators.rule_validator import RuleValidator
from validators.exceptions import BusinessValidationError


@pytest.mark.asyncio
async def test_validation_engine_passed():
    engine = ValidationEngine()
    rewritten = {
        "summary": "Experienced Senior Engineer specializing in Python, FastAPI microservices, and Docker.",
        "experience": [
            {
                "company": "TechCorp",
                "role": "Software Engineer",
                "start_date": "2021-01",
                "end_date": "2023-12",
            }
        ],
    }
    canonical = {"experience": [{"company": "TechCorp"}]}

    report = await engine.validate(rewritten, canonical)

    assert report.status == "PASSED"
    assert report.checks_run >= 2
    assert len(report.violations) == 0


@pytest.mark.asyncio
async def test_validation_engine_failed_date_sequence():
    engine = ValidationEngine()
    invalid_rewritten = {
        "summary": "Experienced engineer.",
        "experience": [
            {
                "company": "TechCorp",
                "role": "Software Engineer",
                "start_date": "2023-12",
                "end_date": "2021-01",  # Start date after end date
            }
        ],
    }
    canonical = {"experience": [{"company": "TechCorp"}]}

    with pytest.raises(BusinessValidationError) as exc_info:
        await engine.validate(invalid_rewritten, canonical)

    assert exc_info.value.report.status == "FAILED"
    assert any(v.code == "BUSINESS_RULE_INVALID_DATE_SEQUENCE" for v in exc_info.value.violations)
