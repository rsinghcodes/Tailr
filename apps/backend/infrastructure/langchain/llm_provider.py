import logging
from typing import Any, Optional, Type, TypeVar
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from config.settings import settings
from domain.shared.llm_provider import LLMProvider
from domain.shared.exceptions import (
    LLMProviderError,
    LLMProviderTimeoutError,
    LLMValidationError,
)

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Concrete LLMProvider wrapping LangChain's ChatGoogleGenerativeAI."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ):
        self.default_model = model or settings.GEMINI_MODEL
        self._llm = ChatGoogleGenerativeAI(
            model=self.default_model,
            google_api_key=api_key or settings.GEMINI_API_KEY,
            temperature=temperature,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[T]] = None,
        temperature: float = 0.0,
        model: Optional[str] = None,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Any:
        target_schema = schema or response_model

        messages: list = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        try:
            if target_schema:
                llm = self._llm.with_structured_output(target_schema)
                result = await llm.ainvoke(messages)
                return result

            result = await self._llm.ainvoke(messages)
            return result.content

        except Exception as exc:
            error_msg = str(exc)
            if "timeout" in error_msg.lower():
                raise LLMProviderTimeoutError(
                    f"Gemini request timed out: {error_msg}"
                ) from exc
            if "validation" in error_msg.lower() or "schema" in error_msg.lower():
                raise LLMValidationError(
                    f"Gemini response failed validation: {error_msg}"
                ) from exc
            raise LLMProviderError(f"Gemini request failed: {error_msg}") from exc

    async def close(self) -> None:
        pass
