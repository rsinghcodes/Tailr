import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies.auth import get_current_user
from api.dependencies.services import get_vector_store_service
from infrastructure.llamaindex.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Knowledge Base & Search"], dependencies=[Depends(get_current_user)]
)


class IndexKnowledgeRequest(BaseModel):
    resume_id: str
    content: str


class IndexKnowledgeResponse(BaseModel):
    status: str = "indexed"
    chunks_indexed: int = 0


class SearchKnowledgeRequest(BaseModel):
    query: str
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
    vector_store: VectorStoreService = Depends(get_vector_store_service),
):
    try:
        context = await vector_store.query_context(body.content, top_k=1)
        indexed = 1 if context and context != "No relevant context found." else 0
        return IndexKnowledgeResponse(status="indexed", chunks_indexed=indexed)
    except Exception as exc:
        logger.error("Knowledge indexing failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(exc)}")


@router.post("/knowledge/search", response_model=SearchKnowledgeResponse)
async def search_knowledge_base(
    body: SearchKnowledgeRequest,
    vector_store: VectorStoreService = Depends(get_vector_store_service),
):
    try:
        context_text = await vector_store.query_context(body.query, top_k=body.limit)
        if not context_text or context_text == "No relevant context found.":
            return SearchKnowledgeResponse(results=[])

        results = []
        for idx, line in enumerate(context_text.split("\n\n")):
            if not line.strip():
                continue
            score = 0.0
            if line.startswith("[score:"):
                try:
                    score = float(line.split("]")[0].replace("[score:", "").strip())
                    line = line.split("]", 1)[1].strip()
                except (ValueError, IndexError):
                    pass
            results.append(
                SearchResultItem(
                    chunk_id=f"chunk-{idx}",
                    content=line.strip(),
                    score=score,
                    entity_type="resume",
                )
            )
        return SearchKnowledgeResponse(results=results)
    except Exception as exc:
        logger.error("Knowledge search failed: %s", str(exc))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")
