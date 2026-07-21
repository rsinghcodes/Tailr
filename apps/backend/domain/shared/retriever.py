from abc import ABC, abstractmethod
from typing import Any, Optional
from domain.shared.vector_store import RetrievalResult


class Retriever(ABC):
    """Abstract base class defining the contract for semantic and lexical document retrieval."""

    @abstractmethod
    async def retrieve(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
        filter_dict: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Retrieves relevant knowledge chunks matching a search query.

        Args:
            collection_name: The target vector storage collection.
            query: The search query text.
            limit: Maximum number of retrieved documents (default: 5).
            filter_dict: Optional metadata field key-value filters.

        Returns:
            A list of RetrievalResult objects.
        """
        pass
