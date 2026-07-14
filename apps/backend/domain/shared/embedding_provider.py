from abc import ABC, abstractmethod
from typing import Optional


class EmbeddingProvider(ABC):
    """Abstract base class defining the contract for generating text embeddings."""

    @abstractmethod
    async def generate_embedding(self, text: str, model: Optional[str] = None) -> list[float]:
        """Generates a dense vector embedding for a single text.

        Args:
            text: The text string to embed.
            model: Optional model override.

        Returns:
            A list of floats representing the embedding vector.
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: list[str], model: Optional[str] = None) -> list[list[float]]:
        """Generates dense vector embeddings for a list of texts.

        Args:
            texts: A list of text strings to embed.
            model: Optional model override.

        Returns:
            A list of float lists representing the embedding vectors.
        """
        pass
