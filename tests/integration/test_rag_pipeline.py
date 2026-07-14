import pytest
import uuid
from unittest.mock import MagicMock
from domain.resume.models import Resume, Experience, ExperienceBullet, Project, Skill, SkillCategory
from domain.shared.embedding_provider import EmbeddingProvider
from domain.shared.llm_provider import LLMProvider
from prompts.registry import PromptRegistry
from infrastructure.qdrant.vector_store import QdrantVectorStore
from rag.chunking.chunker import ResumeChunker
from rag.indexing.indexer import ResumeIndexer
from rag.retrieval.retriever import HybridRetriever
from rag.retrieval.reranker import LLMReranker, ChunkRelevance
from rag.retrieval.context_builder import ContextBuilder
from rag.pipeline import RAGPipeline


@pytest.mark.asyncio
async def test_rag_pipeline_end_to_end():
    # Setup mock embedding provider returning custom vectors based on content keywords
    async def mock_embed_text(text: str, model=None) -> list[float]:
        # Heavy on first dimension for Backend, second for Frontend
        if any(w in text.lower() for w in ["python", "backend", "fastapi"]):
            return [0.9, 0.1, 0.0]
        elif any(w in text.lower() for w in ["react", "frontend", "tailwind"]):
            return [0.1, 0.9, 0.0]
        return [0.3, 0.3, 0.4]

    async def mock_embed_texts(texts: list[str], model=None) -> list[list[float]]:
        return [await mock_embed_text(t) for t in texts]

    embed_provider = MagicMock(spec=EmbeddingProvider)
    embed_provider.generate_embedding.side_effect = mock_embed_text
    embed_provider.generate_embeddings.side_effect = mock_embed_texts

    # Setup mock LLM provider for reranking
    async def mock_generate(prompt: str, system_prompt=None, schema=None, **kwargs):
        # If "Role: Python" is in prompt, rate highly
        if "Role: Python" in prompt or "FastAPI" in prompt:
            return ChunkRelevance(score=5, reason="Excellent backend Python skills match")
        elif "Project: User Interface" in prompt:
            return ChunkRelevance(score=2, reason="Mild overlap with React layouts")
        return ChunkRelevance(score=0, reason="No overlap")

    llm_provider = MagicMock(spec=LLMProvider)
    llm_provider.generate.side_effect = mock_generate

    # Initialize components
    chunker = ResumeChunker()
    
    # Use real Qdrant store pointing to Settings configurations
    store = QdrantVectorStore()
    
    indexer = ResumeIndexer(vector_store=store, embedding_provider=embed_provider)
    retriever = HybridRetriever(vector_store=store, embedding_provider=embed_provider)
    
    prompt_registry = PromptRegistry()
    reranker = LLMReranker(llm_provider=llm_provider, prompt_registry=prompt_registry)
    context_builder = ContextBuilder()

    pipeline = RAGPipeline(
        chunker=chunker,
        indexer=indexer,
        retriever=retriever,
        reranker=reranker,
        context_builder=context_builder
    )

    # 1. Create a dummy test resume
    resume = Resume(
        summary="Experienced Software Engineer",
        skills=[
            Skill(name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE),
            Skill(name="React", category=SkillCategory.FRONTEND)
        ],
        experience=[
            Experience(
                company="BackCorp",
                role="Python Developer",
                start_date="2020-01",
                end_date="2022-12",
                technologies=["Python", "FastAPI"],
                bullets=[ExperienceBullet(text="Built backend REST APIs using FastAPI.")]
            )
        ],
        projects=[
            Project(
                title="User Interface Hub",
                description="Designed React interface dashboards.",
                technologies=["React", "Tailwind"],
                bullets=["Developed modular UI hooks."]
            )
        ]
    )

    # Collection identifier
    collection_name = f"test_rag_pipeline_{uuid.uuid4().hex}"

    try:
        # 2. Index the Resume
        await pipeline.index_resume(collection_name, resume)

        # 3. Retrieve Context matching "Python Developer"
        requirements_text = "Required: Python, FastAPI API engineering."
        context_block = await pipeline.retrieve_context(
            collection_name=collection_name,
            query="Python FastAPI Backend",
            requirements_text=requirements_text,
            limit=2,
            rerank_threshold=2.0
        )

        assert "### Candidate Resume Context" in context_block
        assert "Role: Python Developer" in context_block
        assert "Excellent backend Python skills match" in context_block

    finally:
        # Clean up the test collection on Qdrant Cloud
        await store.delete_collection(collection_name)
