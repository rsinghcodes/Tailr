import logging
import uuid
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from config.settings import settings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "models/embedding-001"
EMBEDDING_DIM = 768
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


class VectorStoreService:
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection: Optional[str] = None,
    ):
        self._url = url or settings.QDRANT_URL
        self._api_key = api_key or settings.QDRANT_API_KEY
        self._collection = collection or settings.QDRANT_COLLECTION
        self._client: AsyncQdrantClient | None = None
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
        )
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        self._collection_initialized = False

    async def _ensure_client(self) -> AsyncQdrantClient:
        if self._client is None:
            self._client = AsyncQdrantClient(url=self._url, api_key=self._api_key)
        return self._client

    async def _ensure_collection(self) -> None:
        if self._collection_initialized:
            return
        client = await self._ensure_client()
        collections = await client.get_collections()
        names = {c.name for c in collections.collections}
        if self._collection not in names:
            await client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            logger.info("Created Qdrant collection '%s'", self._collection)
        self._collection_initialized = True

    async def index_document(self, text: str, filename: str = "document.txt") -> bool:
        try:
            await self._ensure_collection()
            client = await self._ensure_client()

            chunks = self._text_splitter.split_text(text)
            if not chunks:
                logger.warning("No chunks produced for '%s'", filename)
                return False

            embeddings = await self._embeddings.aembed_documents(chunks)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=emb,
                    payload={"filename": filename, "chunk_index": i, "text": chunk},
                )
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
            ]

            await client.upsert(collection_name=self._collection, points=points)
            logger.info("Indexed %d chunks from '%s' to Qdrant '%s'", len(chunks), filename, self._collection)
            return True
        except Exception as exc:
            logger.error("Failed to index document '%s': %s", filename, str(exc))
            return False

    async def query_context(self, query: str, top_k: int = 5) -> str:
        try:
            await self._ensure_collection()
            client = await self._ensure_client()

            query_vector = await self._embeddings.aembed_query(query)

            results = await client.search(
                collection_name=self._collection,
                query_vector=query_vector,
                limit=top_k,
            )

            if not results:
                return "No relevant context found."

            parts = []
            for r in results:
                text = r.payload.get("text", "") if r.payload else ""
                parts.append(f"[score: {r.score:.2f}] {text}")
            return "\n\n".join(parts)
        except Exception as exc:
            logger.error("Qdrant retrieval failed: %s", str(exc))
            return "No relevant context found."
