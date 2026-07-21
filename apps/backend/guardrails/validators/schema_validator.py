import time
from typing import Any, Type
from pydantic import BaseModel, ValidationError
from guardrails.base import (
    BaseValidator,
    GuardrailContext,
    GuardrailResult,
    GuardrailResultStatus,
    GuardrailViolation,
    ViolationSeverity,
)


class SchemaValidator(BaseValidator):
    name: str = "schema_validator"

    def __init__(self, target_schema: Type[BaseModel] | None = None):
        self.target_schema = target_schema

    async def validate(self, content: Any, context: GuardrailContext) -> GuardrailResult:
        start_time = time.perf_counter()

        schema_class = self.target_schema or context.metadata.get("target_schema")

        if not schema_class or not issubclass(schema_class, BaseModel):
            # No target schema specified, pass through
            return GuardrailResult(
                status=GuardrailResultStatus.APPROVED,
                repaired_content=content,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        try:
            if isinstance(content, dict):
                validated_model = schema_class.model_validate(content)
            elif isinstance(content, schema_class):
                validated_model = content
            else:
                validated_model = schema_class.model_validate_json(str(content))

            return GuardrailResult(
                status=GuardrailResultStatus.APPROVED,
                repaired_content=validated_model.model_dump(),
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )
        except ValidationError as err:
            violations = [
                GuardrailViolation(
                    code="SCHEMA_VALIDATION_ERROR",
                    message=f"Field '{'.'.join(str(loc) for loc in error['loc'])}': {error['msg']}",
                    severity=ViolationSeverity.HIGH,
                    field=".".join(str(loc) for loc in error["loc"]),
                )
                for error in err.errors()
            ]
            return GuardrailResult(
                status=GuardrailResultStatus.REJECTED,
                violations=violations,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )
