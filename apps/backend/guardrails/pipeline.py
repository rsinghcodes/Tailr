import time
from typing import Any
from guardrails.base import (
    BaseValidator,
    GuardrailContext,
    GuardrailResult,
    GuardrailResultStatus,
    GuardrailViolation,
)
from guardrails.validators.json_validator import JSONValidator
from guardrails.validators.schema_validator import SchemaValidator
from guardrails.validators.prompt_injection_validator import PromptInjectionValidator
from guardrails.validators.hallucination_validator import HallucinationValidator
from guardrails.validators.resume_validator import ResumeValidator
from guardrails.validators.pii_validator import PIIValidator
from guardrails.validators.ats_validator import ATSValidator
from guardrails.validators.latex_safety_validator import LatexSafetyValidator


class GuardrailsEngine:
    """Mandatory Guardrails Engine & Trust Boundary for AI Outputs."""

    PROFILES: dict[str, list[BaseValidator]] = {
        "rewrite_strict": [
            JSONValidator(),
            PromptInjectionValidator(),
            HallucinationValidator(),
            ResumeValidator(),
            PIIValidator(),
            ATSValidator(),
            LatexSafetyValidator(),
        ],
        "analysis_standard": [
            JSONValidator(),
            PromptInjectionValidator(),
            PIIValidator(),
        ],
        "validation_paranoid": [
            JSONValidator(),
            SchemaValidator(),
            PromptInjectionValidator(),
            HallucinationValidator(),
            ResumeValidator(),
            PIIValidator(),
            ATSValidator(),
            LatexSafetyValidator(),
        ],
    }

    def __init__(self, validators: list[BaseValidator] | None = None):
        self.custom_validators = validators

    async def execute(
        self,
        content: Any,
        context: GuardrailContext,
        profile_name: str | None = None,
    ) -> GuardrailResult:
        start_time = time.perf_counter()
        profile = profile_name or context.profile_name or "rewrite_strict"

        validators_to_run = self.custom_validators or self.PROFILES.get(profile, self.PROFILES["rewrite_strict"])

        current_content = content
        all_violations: list[GuardrailViolation] = []
        all_warnings: list[str] = []
        is_repaired = False

        for validator in validators_to_run:
            res = await validator.validate(current_content, context)

            if res.status == GuardrailResultStatus.REJECTED:
                all_violations.extend(res.violations)
                # Fail Closed on first critical rejection
                return GuardrailResult(
                    status=GuardrailResultStatus.REJECTED,
                    repaired=is_repaired,
                    violations=all_violations,
                    warnings=all_warnings,
                    execution_time_ms=(time.perf_counter() - start_time) * 1000,
                    metadata={"profile": profile, "failed_validator": validator.name},
                )

            if res.status == GuardrailResultStatus.REPAIRED:
                is_repaired = True
                current_content = res.repaired_content
                all_warnings.extend(res.warnings)

            if res.repaired_content is not None:
                current_content = res.repaired_content

        final_status = GuardrailResultStatus.REPAIRED if is_repaired else GuardrailResultStatus.APPROVED

        return GuardrailResult(
            status=final_status,
            repaired=is_repaired,
            violations=[],
            warnings=all_warnings,
            repaired_content=current_content,
            execution_time_ms=(time.perf_counter() - start_time) * 1000,
            metadata={"profile": profile, "validator_count": len(validators_to_run)},
        )
