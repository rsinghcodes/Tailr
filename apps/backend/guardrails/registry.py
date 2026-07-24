from typing import Type
from guardrails.base import BaseValidator
from guardrails.pipeline import GuardrailsEngine


class GuardrailRegistry:
    """Registry for managing custom and standard Guardrail validators."""

    _validators: dict[str, Type[BaseValidator]] = {}

    @classmethod
    def register(cls, name: str, validator_cls: Type[BaseValidator]) -> None:
        cls._validators[name] = validator_cls

    @classmethod
    def get_validator(cls, name: str) -> Type[BaseValidator] | None:
        return cls._validators.get(name)

    @classmethod
    def create_engine(cls, profile_name: str = "rewrite_strict") -> GuardrailsEngine:
        return GuardrailsEngine()
