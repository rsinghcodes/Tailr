import logging
from typing import Any, Optional
from domain.resume.models import Resume
from domain.shared.retriever import Retriever
from rag.chunking.chunker import ResumeChunker
from rag.indexing.indexer import ResumeIndexer
from rag.retrieval.reranker import LLMReranker
from rag.retrieval.context_builder import ContextBuilder

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Unified pipeline coordinating chunking, embedding, indexing, hybrid retrieval, and reranking."""

    def __init__(
        self,
        chunker: ResumeChunker,
        indexer: ResumeIndexer,
        retriever: Retriever,
        reranker: LLMReranker,
        context_builder: ContextBuilder,
    ):
        """Initializes the unified RAG pipeline.

        Args:
            chunker: The resume semantic chunking service.
            indexer: The vector store indexing service.
            retriever: The hybrid search retriever.
            reranker: The LLM reranking scorer.
            context_builder: The markdown format builder.
        """
        self.chunker = chunker
        self.indexer = indexer
        self.retriever = retriever
        self.reranker = reranker
        self.context_builder = context_builder

    async def index_resume(self, collection_name: str, resume: Resume) -> None:
        """Decomposes and indexes a resume into the vector database.

        Args:
            collection_name: The destination vector collection.
            resume: The canonical Resume domain model.
        """
        logger.info("Starting indexing for resume %s in collection %s", str(resume.id), collection_name)
        chunks = self.chunker.chunk_resume(resume)
        await self.indexer.index_chunks(collection_name, chunks)
        logger.info("Successfully indexed %d chunks for resume %s", len(chunks), str(resume.id))

    async def retrieve_context(
        self,
        collection_name: str,
        query: str,
        requirements_text: str,
        limit: int = 5,
        rerank_threshold: float = 2.0,
        model: Optional[str] = None,
    ) -> str:
        """Runs hybrid search, evaluates relevance via LLM, and formats the output block.

        Args:
            collection_name: The target vector collection.
            query: The text search query (e.g. keywords/skills).
            requirements_text: Detailed target requirements for reranker scoring.
            limit: Maximum number of chunks to return (default: 5).
            rerank_threshold: Minimum LLM relevance score threshold (default: 2.0).
            model: Optional LLM model override for reranking.

        Returns:
            A serialized markdown context block ready for prompt formatting.
        """
        logger.info("Retrieving context from collection %s matching query: %s", collection_name, query)
        
        # 1. Run hybrid search (Semantic + BM25)
        retrieved_results = await self.retrieve_chunks(collection_name, query, limit=limit * 2)
        if not retrieved_results:
            return "No relevant context found from the candidate's resume."

        # 2. Extract chunks for reranking
        candidate_chunks = [res.chunk for res in retrieved_results]

        # 3. LLM Reranking
        logger.info("Reranking %d candidate chunks using LLM", len(candidate_chunks))
        reranked_results = await self.reranker.rerank(
            chunks=candidate_chunks,
            requirements=requirements_text,
            threshold=rerank_threshold,
            model=model
        )

        # 4. Limit to final requested size
        final_results = reranked_results[:limit]
        logger.info("Reranked results count: %d after filtering threshold %s", len(final_results), str(rerank_threshold))

        # 5. Format Context Block
        return self.context_builder.build_context(final_results)

    async def retrieve_chunks(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
    ) -> list[Any]:
        """Low-level helper to run hybrid search without reranking.

        Args:
            collection_name: The target collection.
            query: The query text.
            limit: Maximum retrieval count.

        Returns:
            A list of RetrievalResult objects.
        """
        try:
            return await self.retriever.retrieve(collection_name, query, limit=limit)
        except Exception as exc:
            logger.error("Hybrid search failed on collection %s: %s", collection_name, str(exc))
            return []
