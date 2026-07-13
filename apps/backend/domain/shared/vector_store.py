import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    source: str
    importance: float
    technologies: list[str] = Field(default_factory=list)
    category: str
    verified: bool = False


class KnowledgeChunk(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    entity_type: str
    entity_id: uuid.UUID
    metadata: ChunkMetadata


class RetrievalResult(BaseModel):
    chunk: KnowledgeChunk
    score: float
    rerank_score: Optional[float] = None
    reason: Optional[str] = None


class VectorStore(ABC):
    @abstractmethod
    async def create_collection(self, collection_name: str, vector_size: int) -> None:
        """Create a collection in the vector database."""
        pass

    @abstractmethod
    async def upsert_chunks(
        self,
        collection_name: str,
        chunks: list[KnowledgeChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Upsert a list of chunks and their corresponding embeddings into the collection."""
        pass

    @abstractmethod
    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        filter_dict: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Search the collection semantically using a query vector."""
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection from the vector database."""
        pass
