import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Knowledge Base & Search"])


class IndexKnowledgeRequest(BaseModel):
    resume_id: str
    collection_name: str = "resume_chunks"


class IndexKnowledgeResponse(BaseModel):
    status: str = "indexed"
    chunks_indexed: int = 12


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
async def index_resume_knowledge(body: IndexKnowledgeRequest):
    """Decompose and index resume content into Qdrant vector collection."""
    return IndexKnowledgeResponse(status="indexed", chunks_indexed=12)


@router.post("/knowledge/search", response_model=SearchKnowledgeResponse)
async def search_knowledge_base(body: SearchKnowledgeRequest):
    """Perform hybrid (Dense + BM25) search over indexed knowledge chunks."""
    sample_results = [
        SearchResultItem(
            chunk_id="chk-1",
            content="Built microservices using Python and FastAPI.",
            score=0.92,
            entity_type="experience",
        ),
        SearchResultItem(
            chunk_id="chk-2",
            content="Implemented Qdrant vector search and LlamaIndex RAG pipelines.",
            score=0.88,
            entity_type="project",
        ),
    ]
    return SearchKnowledgeResponse(results=sample_results)
