import json
import logging
from typing import Any, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from domain.shared.llm_provider import LLMProvider
from domain.shared.exceptions import (
    LLMProviderError,
    LLMProviderTimeoutError,
    LLMValidationError,
)

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama API provider connecting directly to local Docker/host Ollama instance."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "qwen3:8b",
        client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.client = client or httpx.AsyncClient(base_url=self.base_url, timeout=httpx.Timeout(300.0))

    async def close(self) -> None:
        """Closes the underlying HTTPX async client."""
        await self.client.aclose()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[T]] = None,
        temperature: float = 0.0,
        model: Optional[str] = None,
        timeout: float = 300.0,
        **kwargs: Any,
    ) -> Any:
        target_schema = schema or kwargs.pop("response_model", None)
        target_model = model or self.default_model

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs,
            },
        }

        if target_schema:
            payload["format"] = "json"

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

        if not target_schema:
            return content

        try:
            parsed_json = json.loads(content)
            return target_schema.model_validate(parsed_json)
        except Exception as exc:
            logger.warning("Failed to validate Ollama response against schema: %s", str(exc))
            raise LLMValidationError(f"Response validation failed for {target_schema.__name__}: {str(exc)}") from exc
