from typing import Any, Optional
from domain.shared.retriever import Retriever
from domain.shared.vector_store import VectorStore, RetrievalResult
from domain.shared.embedding_provider import EmbeddingProvider
from rag.retrieval.bm25 import BM25Scorer


class HybridRetriever(Retriever):
    """Concrete Retriever adapter combining Qdrant semantic search and BM25 lexical ranking."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
        semantic_weight: float = 0.7,
        rrf_k: int = 60,
    ):
        """Initializes the hybrid retriever.

        Args:
            vector_store: The storage client where chunks are indexed.
            embedding_provider: The embedding model to vectorize query texts.
            semantic_weight: Weight assigned to semantic ranking (used if linear blending).
            rrf_k: Reciprocal Rank Fusion constant parameter (default: 60).
        """
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.semantic_weight = semantic_weight
        self.rrf_k = rrf_k

    async def retrieve(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
        filter_dict: Optional[dict[str, Any]] = None,
    ) -> list[RetrievalResult]:
        """Retrieves and merges chunks using both semantic similarity and BM25 lexical matches.

        Args:
            collection_name: The destination vector collection.
            query: The search text query.
            limit: Maximum number of merged results to return.
            filter_dict: Optional metadata field filters.

        Returns:
            A list of merged and ranked RetrievalResult objects.
        """
        # Fetch candidate pool (limit * 3 to ensure overlapping ranks can resolve)
        candidate_limit = limit * 3

        # 1. Semantic Retrieval
        query_vector = await self.embedding_provider.generate_embedding(query)
        semantic_results = await self.vector_store.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=candidate_limit,
            filter_dict=filter_dict
        )

        if not semantic_results:
            return []

        # 2. Lexical BM25 Scoring on retrieved candidates
        corpus = [res.chunk.content for res in semantic_results]
        bm25_scorer = BM25Scorer(corpus)
        bm25_scores = bm25_scorer.score(query)

        # 3. Reciprocal Rank Fusion (RRF)
        # Create rank list for semantic results
        semantic_ranked = [res.chunk.id for res in semantic_results]
        
        # Sort candidates by BM25 score to get BM25 ranks
        candidates_with_bm25 = sorted(
            zip(semantic_results, bm25_scores),
            key=lambda x: x[1],
            reverse=True
        )
        bm25_ranked = [item[0].chunk.id for item in candidates_with_bm25]

        # Calculate RRF score for each chunk
        rrf_scores: dict[Any, float] = {}
        chunk_map = {res.chunk.id: res for res in semantic_results}

        for chunk_id in chunk_map.keys():
            # Get semantic rank index (1-based)
            sem_rank = semantic_ranked.index(chunk_id) + 1
            # Get BM25 rank index (1-based)
            bm25_rank = bm25_ranked.index(chunk_id) + 1

            # RRF Fusion formula
            rrf_score = (1.0 / (self.rrf_k + sem_rank)) + (1.0 / (self.rrf_k + bm25_rank))
            rrf_scores[chunk_id] = rrf_score

        # Sort chunk IDs by their fused RRF score descending
        sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        # Build final merged results
        fused_results = []
        for cid in sorted_chunk_ids[:limit]:
            original_result = chunk_map[cid]
            # Replace score with combined RRF score
            fused_results.append(
                RetrievalResult(
                    chunk=original_result.chunk,
                    score=rrf_scores[cid],
                    reason="Hybrid Fusion (Semantic + BM25)"
                )
            )

        return fused_results
