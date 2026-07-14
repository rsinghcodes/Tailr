from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract base class defining the contract for LLM text generation and structured outputs."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[T]] = None,
        temperature: float = 0.0,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Generates a text or structured response from the LLM.

        Args:
            prompt: The user input prompt.
            system_prompt: Optional system prompt to instruct the model.
            schema: Optional Pydantic model class to parse/validate the output structure.
            temperature: Sampling temperature (default: 0.0).
            model: Optional model override.
            **kwargs: Additional parameters for the provider implementation.

        Returns:
            The raw text string, or an instance of the requested Pydantic schema if provided.
        """
        pass
