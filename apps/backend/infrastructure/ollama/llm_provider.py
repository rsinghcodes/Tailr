import json
import logging
from typing import Any, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError
from config.settings import settings
from domain.shared.llm_provider import LLMProvider
from domain.shared.exceptions import LLMProviderError, LLMProviderTimeoutError, LLMValidationError

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Concrete LLMProvider adapter that connects to local or containerized Ollama services."""

    def __init__(self, base_url: Optional[str] = None, default_model: str = "qwen2.5:7b-instruct"):
        """Initializes the Ollama provider.

        Args:
            base_url: Optional base URL of the Ollama server. Falls back to settings.OLLAMA_URL.
            default_model: The default model to use for generation (default: qwen2.5:7b-instruct).
        """
        self.base_url = base_url or settings.OLLAMA_URL
        self.default_model = default_model
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[T]] = None,
        temperature: float = 0.0,
        model: Optional[str] = None,
        timeout: float = 60.0,
        **kwargs: Any,
    ) -> Any:
        """Generates a text or structured response from Ollama.

        Args:
            prompt: The user input prompt.
            system_prompt: Optional system prompt to instruct the model.
            schema: Optional Pydantic model class to parse/validate the output structure.
            temperature: Sampling temperature (default: 0.0).
            model: Optional model override.
            timeout: HTTP request timeout in seconds (default: 60.0).
            **kwargs: Additional parameters passed to Ollama options.

        Returns:
            The raw text string, or an instance of the requested Pydantic schema if provided.

        Raises:
            LLMProviderTimeoutError: If the Ollama request times out.
            LLMProviderError: If any other request or system error occurs.
            LLMValidationError: If the response fails validation against the Pydantic schema.
        """
        target_model = model or self.default_model

        # Build messages list
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Build request payload
        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs,
            },
        }

        # Handle structured outputs
        if schema:
            payload["format"] = schema.model_json_schema()

        try:
            response = await self.client.post("/api/chat", json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            logger.error("Ollama request timed out: %s", str(exc))
            raise LLMProviderTimeoutError(f"Ollama request to model {target_model} timed out.") from exc
        except httpx.HTTPError as exc:
            logger.error("Ollama request failed: %s", str(exc))
            raise LLMProviderError(f"Ollama request failed: {str(exc)}") from exc
        except Exception as exc:
            logger.error("Unexpected error in Ollama generation: %s", str(exc))
            raise LLMProviderError(f"Unexpected error in Ollama generation: {str(exc)}") from exc

        message = data.get("message", {})
        content = message.get("content", "").strip()

        if not schema:
            return content

        try:
            parsed_json = json.loads(content)
            return schema.model_validate(parsed_json)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.error("Ollama response failed schema validation. Content: %s, Error: %s", content, str(exc))
            raise LLMValidationError(
                f"Failed to validate response against Pydantic schema: {str(exc)}. Content: {content}"
            ) from exc

    async def close(self) -> None:
        """Closes the underlying HTTPX client session."""
        await self.client.aclose()
