import logging
from typing import Optional
import httpx
from config.settings import settings
from domain.shared.embedding_provider import EmbeddingProvider
from domain.shared.exceptions import LLMProviderError, LLMProviderTimeoutError

logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Concrete EmbeddingProvider adapter that connects to local or containerized Ollama embedding services."""

    def __init__(self, base_url: Optional[str] = None, default_model: str = "nomic-embed-text"):
        """Initializes the Ollama embedding provider.

        Args:
            base_url: Optional base URL of the Ollama server. Falls back to settings.OLLAMA_URL.
            default_model: The default embedding model to use (default: nomic-embed-text).
        """
        self.base_url = base_url or settings.OLLAMA_URL
        self.default_model = default_model
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def generate_embedding(self, text: str, model: Optional[str] = None) -> list[float]:
        """Generates a dense vector embedding for a single text.

        Args:
            text: The text string to embed.
            model: Optional model override.

        Returns:
            A list of floats representing the embedding vector.

        Raises:
            LLMProviderTimeoutError: If the request times out.
            LLMProviderError: If any other request or system error occurs.
        """
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "prompt": text,
        }

        try:
            response = await self.client.post("/api/embeddings", json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            embedding = data.get("embedding", [])
            if not embedding:
                raise LLMProviderError("No embedding vector returned in Ollama response.")
            return embedding
        except httpx.TimeoutException as exc:
            logger.error("Ollama embedding request timed out: %s", str(exc))
            raise LLMProviderTimeoutError(f"Embedding request to model {target_model} timed out.") from exc
        except httpx.HTTPError as exc:
            logger.error("Ollama embedding request failed: %s", str(exc))
            raise LLMProviderError(f"Ollama embedding request failed: {str(exc)}") from exc
        except Exception as exc:
            logger.error("Unexpected error in Ollama embedding: %s", str(exc))
            raise LLMProviderError(f"Unexpected error in Ollama embedding: {str(exc)}") from exc

    async def generate_embeddings(self, texts: list[str], model: Optional[str] = None) -> list[list[float]]:
        """Generates dense vector embeddings for a list of texts using batch /api/embed or sequential fallback.

        Args:
            texts: A list of text strings to embed.
            model: Optional model override.

        Returns:
            A list of float lists representing the embedding vectors.

        Raises:
            LLMProviderTimeoutError: If any request times out.
            LLMProviderError: If any other request or system error occurs.
        """
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "input": texts,
        }

        # Try newer batch endpoint `/api/embed` first
        try:
            response = await self.client.post("/api/embed", json=payload, timeout=60.0)
            if response.status_code == 200:
                data = response.json()
                embeddings = data.get("embeddings", [])
                if embeddings:
                    return embeddings
        except httpx.TimeoutException as exc:
            logger.error("Ollama batch embedding request timed out: %s", str(exc))
            raise LLMProviderTimeoutError(f"Batch embedding request to model {target_model} timed out.") from exc
        except Exception:
            # Catch other exceptions and fallback to sequential endpoint
            pass

        # Fallback: sequential queries to `/api/embeddings`
        logger.info("Batch endpoint `/api/embed` unavailable, falling back to sequential calls.")
        results = []
        for text in texts:
            emb = await self.generate_embedding(text, model=target_model)
            results.append(emb)
        return results

    async def close(self) -> None:
        """Closes the underlying HTTPX client session."""
        await self.client.aclose()
