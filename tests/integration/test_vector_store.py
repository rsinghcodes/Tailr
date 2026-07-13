import pytest
import uuid
from domain.shared.vector_store import KnowledgeChunk, ChunkMetadata
from infrastructure.qdrant.vector_store import QdrantVectorStore


@pytest.mark.asyncio
async def test_qdrant_vector_store_operations():
    # Initialize the concrete vector store adapter
    store = QdrantVectorStore()

    # Generate a unique temporary collection name
    collection_name = f"test_collection_{uuid.uuid4().hex}"
    vector_size = 3

    try:
        # 1. Create Collection
        await store.create_collection(collection_name, vector_size)

        # 2. Prepare test chunks and embeddings
        chunk1 = KnowledgeChunk(
            id=uuid.uuid4(),
            content="I developed backend APIs using Python and FastAPI.",
            entity_type="Experience",
            entity_id=uuid.uuid4(),
            metadata=ChunkMetadata(
                source="resume",
                importance=0.9,
                technologies=["Python", "FastAPI"],
                category="Backend",
                verified=True
            )
        )

        chunk2 = KnowledgeChunk(
            id=uuid.uuid4(),
            content="I built user interfaces using React and Tailwind.",
            entity_type="Project",
            entity_id=uuid.uuid4(),
            metadata=ChunkMetadata(
                source="resume",
                importance=0.8,
                technologies=["React", "Tailwind"],
                category="Frontend",
                verified=False
            )
        )

        chunks = [chunk1, chunk2]
        embeddings = [
            [0.9, 0.1, 0.1],  # Heavy on first dimension (Backend)
            [0.1, 0.9, 0.1]   # Heavy on second dimension (Frontend)
        ]

        # 3. Upsert Chunks
        await store.upsert_chunks(collection_name, chunks, embeddings)

        # 4. Search Semantically (Query close to Backend vector)
        query_vector_backend = [0.8, 0.2, 0.1]
        results_backend = await store.search(
            collection_name=collection_name,
            query_vector=query_vector_backend,
            limit=2
        )

        assert len(results_backend) == 2
        # The top hit should be chunk1 (Backend)
        assert results_backend[0].chunk.id == chunk1.id
        assert results_backend[0].score > results_backend[1].score

        # 5. Search with Metadata Filter
        # Let's filter specifically for Frontend category
        results_filtered = await store.search(
            collection_name=collection_name,
            query_vector=query_vector_backend,
            limit=2,
            filter_dict={"metadata.category": "Frontend"}
        )

        # Should only return chunk2
        assert len(results_filtered) == 1
        assert results_filtered[0].chunk.id == chunk2.id
        assert results_filtered[0].chunk.metadata.category == "Frontend"

        # 6. Filter on list element (MatchAny on technologies)
        results_tech_filtered = await store.search(
            collection_name=collection_name,
            query_vector=query_vector_backend,
            limit=2,
            filter_dict={"metadata.technologies": ["FastAPI"]}
        )

        assert len(results_tech_filtered) == 1
        assert results_tech_filtered[0].chunk.id == chunk1.id

    finally:
        # Clean up the test collection on Qdrant Cloud
        await store.delete_collection(collection_name)
