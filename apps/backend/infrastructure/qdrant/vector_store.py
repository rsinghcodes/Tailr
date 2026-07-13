import uuid
from typing import Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest_models
from config.settings import settings
from domain.shared.vector_store import VectorStore, KnowledgeChunk, ChunkMetadata, RetrievalResult


class QdrantVectorStore(VectorStore):
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        qdrant_url = url or settings.QDRANT_URL
        qdrant_key = api_key or settings.QDRANT_API_KEY
        
        self.client = AsyncQdrantClient(
            url=qdrant_url,
            api_key=qdrant_key,
        )

    async def create_collection(self, collection_name: str, vector_size: int) -> None:
        exists = await self.client.collection_exists(collection_name)
        if not exists:
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=rest_models.VectorParams(
                    size=vector_size,
                    distance=rest_models.Distance.COSINE
                )
            )
            # Create payload indexes required for filtering in strict environments like Qdrant Cloud
            await self.client.create_payload_index(
                collection_name=collection_name,
                field_name="metadata.category",
                field_schema=rest_models.PayloadSchemaType.KEYWORD
            )
            await self.client.create_payload_index(
                collection_name=collection_name,
                field_name="metadata.technologies",
                field_schema=rest_models.PayloadSchemaType.KEYWORD
            )

    async def upsert_chunks(
        self,
        collection_name: str,
        chunks: list[KnowledgeChunk],
        embeddings: list[list[float]],
    ) -> None:
        points = []
        for chunk, emb in zip(chunks, embeddings):
            points.append(
                rest_models.PointStruct(
                    id=str(chunk.id),
                    vector=emb,
                    payload={
                        "content": chunk.content,
                        "entity_type": chunk.entity_type,
                        "entity_id": str(chunk.entity_id),
                        "metadata": chunk.metadata.model_dump(mode="json")
                    }
                )
            )
        
        await self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        filter_dict: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        qdrant_filter = None
        
        if filter_dict:
            must_filters: list[Any] = []
            for key, val in filter_dict.items():
                if isinstance(val, list):
                    # Match any value in list (Qdrant MatchAny)
                    must_filters.append(
                        rest_models.FieldCondition(
                            key=key,
                            match=rest_models.MatchAny(any=val)
                        )
                    )
                else:
                    must_filters.append(
                        rest_models.FieldCondition(
                            key=key,
                            match=rest_models.MatchValue(value=val)
                        )
                    )
            qdrant_filter = rest_models.Filter(must=must_filters)

        response = await self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            query_filter=qdrant_filter
        )

        results = []
        for hit in response.points:
            payload = hit.payload or {}
            meta_data = payload.get("metadata", {})
            
            hit_id = hit.id
            if isinstance(hit_id, uuid.UUID):
                chunk_id = hit_id
            elif isinstance(hit_id, str):
                chunk_id = uuid.UUID(hit_id)
            elif isinstance(hit_id, int):
                chunk_id = uuid.UUID(int=hit_id)
            else:
                chunk_id = uuid.uuid4()

            chunk = KnowledgeChunk(
                id=chunk_id,
                content=payload.get("content", ""),
                entity_type=payload.get("entity_type", ""),
                entity_id=uuid.UUID(payload.get("entity_id")) if payload.get("entity_id") else uuid.uuid4(),
                metadata=ChunkMetadata(**meta_data)
            )
            
            results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=hit.score
                )
            )
            
        return results

    async def delete_collection(self, collection_name: str) -> None:
        exists = await self.client.collection_exists(collection_name)
        if exists:
            await self.client.delete_collection(collection_name=collection_name)
