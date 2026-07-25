import logging
import time
from typing import Any, Optional
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)


class OllamaHealthChecker:
    """Diagnostic tool to verify connectivity to Ollama Docker container and check available AI models."""

    def __init__(self, base_url: Optional[str] = None):
        """Initializes the Ollama health checker.

        Args:
            base_url: Optional Ollama server URL. Defaults to settings.OLLAMA_URL.
        """
        self.base_url = (base_url or settings.OLLAMA_URL).rstrip("/")

    async def check_health(self) -> dict[str, Any]:
        """Queries Ollama container tags endpoint to verify readiness and model availability.

        Returns:
            Dictionary containing health status, latency (ms), available models, and status flag.
        """
        start_time = time.perf_counter()
        tags_url = f"{self.base_url}/api/tags"

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                response = await client.get(tags_url)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if response.status_code == 200:
                    data = response.json()
                    raw_models = data.get("models", [])
                    model_names = [m.get("name") for m in raw_models if isinstance(m, dict)]

                    # Check for required chat model and embedding model
                    has_chat_model = any("qwen" in m.lower() for m in model_names)
                    has_embed_model = any("embed" in m.lower() or "nomic" in m.lower() for m in model_names)

                    return {
                        "status": "healthy" if (has_chat_model or len(model_names) > 0) else "degraded",
                        "online": True,
                        "latency_ms": latency_ms,
                        "url": self.base_url,
                        "available_models": model_names,
                        "has_chat_model": has_chat_model,
                        "has_embed_model": has_embed_model,
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "online": False,
                        "latency_ms": latency_ms,
                        "url": self.base_url,
                        "error": f"HTTP status {response.status_code}",
                        "available_models": [],
                    }
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning("Ollama container connection failed at %s: %s", self.base_url, str(exc))
            return {
                "status": "offline",
                "online": False,
                "latency_ms": latency_ms,
                "url": self.base_url,
                "error": str(exc),
                "available_models": [],
            }


ollama_health_checker = OllamaHealthChecker()
