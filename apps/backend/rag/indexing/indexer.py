from domain.shared.vector_store import VectorStore, KnowledgeChunk
from domain.shared.embedding_provider import EmbeddingProvider


class ResumeIndexer:
    """Service to generate dense embeddings for KnowledgeChunks and index them in the VectorStore."""

    def __init__(self, vector_store: VectorStore, embedding_provider: EmbeddingProvider):
        """Initializes the resume indexer.

        Args:
            vector_store: The destination vector store.
            embedding_provider: The embedding model provider.
        """
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    async def index_chunks(self, collection_name: str, chunks: list[KnowledgeChunk]) -> None:
        """Generates embeddings and indexes a list of KnowledgeChunks.

        Args:
            collection_name: The destination vector collection.
            chunks: The list of KnowledgeChunks to index.
        """
        if not chunks:
            return

        # 1. Extract text and generate dense vector representations
        texts = [chunk.content for chunk in chunks]
        embeddings = await self.embedding_provider.generate_embeddings(texts)

        if not embeddings or not embeddings[0]:
            raise ValueError("Failed to generate vector embeddings for chunks.")

        # 2. Determine vector dimension size
        vector_size = len(embeddings[0])

        # 3. Create collection and store the documents
        await self.vector_store.create_collection(collection_name, vector_size=vector_size)
        await self.vector_store.upsert_chunks(collection_name, chunks, embeddings)
