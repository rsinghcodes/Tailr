import logging
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.ollama.embedding_provider import OllamaEmbeddingProvider
from infrastructure.qdrant.vector_store import QdrantVectorStore
from infrastructure.redis.cache import RedisCacheService, get_redis_cache_service
from infrastructure.database import get_db
from infrastructure.repositories.resume_repository import ResumeRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Knowledge Base & Search"])

_embedding_provider = OllamaEmbeddingProvider()
_vector_store = QdrantVectorStore()


class IndexKnowledgeRequest(BaseModel):
    resume_id: str
    collection_name: str = "resume_chunks"


class IndexKnowledgeResponse(BaseModel):
    status: str = "indexed"
    chunks_indexed: int = 0


class SearchKnowledgeRequest(BaseModel):
    query: str
    collection_name: str = "resume_chunks"
    limit: int = 10


class SearchResultItem(BaseModel):
    chunk_id: str
    content: str
    score: float
    entity_type: str


class SearchKnowledgeResponse(BaseModel):
    results: list[SearchResultItem] = Field(default_factory=list)


@router.post("/knowledge/index", response_model=IndexKnowledgeResponse)
async def index_resume_knowledge(
    body: IndexKnowledgeRequest,
    session: AsyncSession = Depends(get_db),
):
    """Decompose and index resume content into Qdrant vector collection."""
    try:
        await _vector_store.ensure_collection(body.collection_name, vector_size=768)

        # Fetch resume and create chunks
        repo = ResumeRepositoryImpl(session)
        resume = await repo.get_by_version_id(uuid.UUID(body.resume_id))
        if not resume:
            raise HTTPException(status_code=404, detail=f"Resume '{body.resume_id}' not found.")

        resume_data = resume.model_dump(mode="json")
        chunks = []

        # Chunk by section
        if resume_data.get("summary"):
            chunks.append({"content": resume_data["summary"], "entity_type": "summary"})

        for skill in resume_data.get("skills", []):
            chunks.append({"content": f"Skill: {skill.get('name', '')}", "entity_type": "skill"})

        for exp in resume_data.get("experience", []):
            exp_text = f"{exp.get('role', '')} at {exp.get('company', '')}"
            for bullet in exp.get("bullets", []):
                if isinstance(bullet, dict):
                    exp_text += f". {bullet.get('text', '')}"
                else:
                    exp_text += f". {bullet}"
            chunks.append({"content": exp_text, "entity_type": "experience"})

        for proj in resume_data.get("projects", []):
            chunks.append({"content": f"Project: {proj.get('title', '')} - {proj.get('description', '')}", "entity_type": "project"})

        for edu in resume_data.get("education", []):
            chunks.append({"content": f"Education: {edu.get('degree', '')} from {edu.get('institution', '')}", "entity_type": "education"})

        # Index chunks with embeddings
        indexed = 0
        for i, chunk in enumerate(chunks):
            try:
                embedding = await _embedding_provider.get_embedding(chunk["content"])
                chunk_id = f"{body.resume_id}-chunk-{i}"
                await _vector_store.upsert(
                    collection_name=body.collection_name,
                    id=uuid.uuid4(),
                    vector=embedding,
                    payload={"content": chunk["content"], "entity_type": chunk["entity_type"], "resume_id": body.resume_id},
                )
                indexed += 1
            except Exception as exc:
                logger.warning("Failed to index chunk %d: %s", i, str(exc))

        return IndexKnowledgeResponse(status="indexed", chunks_indexed=indexed)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Knowledge indexing error: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(exc)}") from exc


@router.post("/knowledge/search", response_model=SearchKnowledgeResponse)
async def search_knowledge_base(
    body: SearchKnowledgeRequest,
    cache_service: RedisCacheService = Depends(get_redis_cache_service),
):
    """Perform hybrid search over indexed knowledge chunks."""
    cache_key = f"knowledge_search:{body.collection_name}:{body.query}:{body.limit}"
    cached = await cache_service.get(cache_key, SearchKnowledgeResponse)
    if cached:
        return cached

    try:
        query_vector = await _embedding_provider.get_embedding(body.query)
        hits = await _vector_store.search(
            collection_name=body.collection_name,
            query_vector=query_vector,
            limit=body.limit,
        )

        results = []
        for h in hits:
            payload = h.payload or {}
            results.append(
                SearchResultItem(
                    chunk_id=str(h.id),
                    content=payload.get("content", str(payload)),
                    score=float(h.score),
                    entity_type=payload.get("entity_type", "chunk"),
                )
            )

        response = SearchKnowledgeResponse(results=results)
        await cache_service.set(cache_key, response, ttl_seconds=600)
        return response
    except Exception as exc:
        logger.warning("Vector search failed: %s", str(exc))
        return SearchKnowledgeResponse(results=[])
