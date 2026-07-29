import logging
import time
from typing import Any
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiHealthChecker:
    """Health checker that verifies Gemini API connectivity and key validity."""

    def __init__(self):
        self.model = settings.GEMINI_MODEL

    async def check_health(self) -> dict[str, Any]:
        start_time = time.perf_counter()
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.0,
            )
            await llm.ainvoke([HumanMessage(content="ping")])
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "healthy",
                "online": True,
                "latency_ms": latency_ms,
                "model": self.model,
            }
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning("Gemini API health check failed: %s", str(exc))
            return {
                "status": "offline",
                "online": False,
                "latency_ms": latency_ms,
                "model": self.model,
                "error": str(exc),
            }


gemini_health_checker = GeminiHealthChecker()
