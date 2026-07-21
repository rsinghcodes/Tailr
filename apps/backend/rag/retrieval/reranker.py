import asyncio
import logging
from typing import Optional
from pydantic import BaseModel, Field
from domain.shared.llm_provider import LLMProvider
from domain.shared.vector_store import KnowledgeChunk, RetrievalResult
from prompts.registry import PromptRegistry

logger = logging.getLogger(__name__)


class ChunkRelevance(BaseModel):
    """Pydantic model representing LLM evaluation output for chunk relevance."""
    score: int = Field(..., description="Relevance rating from 0 to 5", ge=0, le=5)
    reason: str = Field(..., description="Brief reasoning explanation for the score")


class LLMReranker:
    """Service to score and rerank KnowledgeChunks using generative LLM assessments."""

    def __init__(self, llm_provider: LLMProvider, prompt_registry: PromptRegistry):
        """Initializes the LLM reranker.

        Args:
            llm_provider: The LLM model client.
            prompt_registry: Central prompt templates directory.
        """
        self.llm_provider = llm_provider
        self.prompt_registry = prompt_registry

    async def rerank_chunk(self, chunk: KnowledgeChunk, requirements: str, model: Optional[str] = None) -> RetrievalResult:
        """Evaluates and scores a single KnowledgeChunk's relevance.

        Args:
            chunk: The KnowledgeChunk to score.
            requirements: The target requirements text.
            model: Optional model override.

        Returns:
            A RetrievalResult containing the chunk, score, and reasoning.
        """
        template = self.prompt_registry.get_prompt("reranker", "rerank", "v1")
        prompt = template.format(requirements=requirements, chunk_content=chunk.content)

        try:
            eval_output: ChunkRelevance = await self.llm_provider.generate(
                prompt=prompt,
                schema=ChunkRelevance,
                temperature=0.0,
                model=model
            )
            return RetrievalResult(
                chunk=chunk,
                score=float(eval_output.score),
                reason=eval_output.reason
            )
        except Exception as exc:
            logger.error("Reranking failed for chunk %s: %s", str(chunk.id), str(exc))
            # Fallback to neutral score of 0
            return RetrievalResult(
                chunk=chunk,
                score=0.0,
                reason=f"Failed to rerank chunk: {str(exc)}"
            )

    async def rerank(
        self,
        chunks: list[KnowledgeChunk],
        requirements: str,
        threshold: float = 2.0,
        model: Optional[str] = None,
    ) -> list[RetrievalResult]:
        """Scores all candidate chunks in parallel and returns filtered, sorted results.

        Args:
            chunks: List of KnowledgeChunks to evaluate.
            requirements: The target requirements text.
            threshold: Minimum score threshold (default: 2.0).
            model: Optional model override.

        Returns:
            A list of sorted RetrievalResult objects meeting the threshold.
        """
        if not chunks:
            return []

        # Run evaluations in parallel to optimize latency
        tasks = [self.rerank_chunk(chunk, requirements, model=model) for chunk in chunks]
        results = await asyncio.gather(*tasks)

        # Filter out low-scoring chunks
        filtered_results = [res for res in results if res.score >= threshold]

        # Sort by score descending
        sorted_results = sorted(filtered_results, key=lambda x: x.score, reverse=True)
        return sorted_results
