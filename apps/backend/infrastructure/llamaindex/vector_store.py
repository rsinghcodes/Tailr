import logging
import uuid
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from config.settings import settings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 3072
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
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM, distance=Distance.COSINE
                ),
            )
            logger.info("Created Qdrant collection '%s'", self._collection)
        self._collection_initialized = True

    async def index_structured_extraction(
        self,
        data: dict,
        source_type: str,
        source_id: str,
    ) -> bool:
        try:
            await self._ensure_collection()
            client = await self._ensure_client()

            sections = _build_sections(data, source_type)
            if not sections:
                logger.warning("No sections produced for '%s'", source_id)
                return False

            all_chunks: list[str] = []
            all_payloads: list[dict] = []

            for section_name, section_text in sections:
                section_chunks = self._text_splitter.split_text(section_text)
                for chunk in section_chunks:
                    all_chunks.append(chunk)
                    all_payloads.append({
                        "section": section_name,
                        "source_id": source_id,
                        "source_type": source_type,
                        "text": chunk,
                    })

            embeddings = await self._embeddings.aembed_documents(all_chunks)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=emb,
                    payload=payload,
                )
                for emb, payload in zip(embeddings, all_payloads)
            ]

            await client.upsert(collection_name=self._collection, points=points)
            logger.info(
                "Indexed %d chunks from %s '%s' to Qdrant '%s'",
                len(all_chunks),
                source_type,
                source_id,
                self._collection,
            )
            return True
        except Exception as exc:
            logger.error(
                "Failed to index structured %s '%s': %s",
                source_type,
                source_id,
                str(exc),
            )
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


def _build_sections(data: dict, source_type: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []

    if source_type == "resume":
        if summary := data.get("summary", ""):
            sections.append(("summary", summary))
        if skills := data.get("skills", []):
            texts = [s.get("name", str(s)) if isinstance(s, dict) else str(s) for s in skills]
            sections.append(("skills", ", ".join(texts)))
        if experience := data.get("experience", []):
            parts = []
            for exp in experience:
                bullets = exp.get("bullets", [])
                bullet_texts = [b.get("text", str(b)) if isinstance(b, dict) else str(b) for b in bullets]
                techs = exp.get("technologies", [])
                line = f"{exp.get('role', '')} at {exp.get('company', '')}"
                if techs:
                    line += f" [{', '.join(techs)}]"
                if bullet_texts:
                    line += ": " + " ".join(bullet_texts)
                parts.append(line)
            sections.append(("experience", "\n".join(parts)))
        if education := data.get("education", []):
            parts = []
            for edu in education:
                line = f"{edu.get('degree', '')} at {edu.get('institution', '')}"
                if edu.get("field"):
                    line += f" ({edu['field']})"
                parts.append(line)
            sections.append(("education", "\n".join(parts)))
        if projects := data.get("projects", []):
            parts = []
            for proj in projects:
                title = proj.get("title", "")
                desc = proj.get("description", "")
                techs = proj.get("technologies", [])
                bullets = proj.get("bullets", [])
                line = title
                if techs:
                    line += f" [{', '.join(techs)}]"
                if desc:
                    line += f": {desc}"
                if bullets:
                    bullet_texts = [b.get("text", str(b)) if isinstance(b, dict) else str(b) for b in bullets]
                    line += " | " + " ".join(bullet_texts)
                parts.append(line)
            sections.append(("projects", "\n".join(parts)))
        if certifications := data.get("certifications", []):
            texts = [c.get("name", str(c)) if isinstance(c, dict) else str(c) for c in certifications]
            sections.append(("certifications", ", ".join(texts)))

    elif source_type == "jd":
        if title := data.get("title", ""):
            sections.append(("title", title))
        if required_skills := data.get("required_skills", []):
            sections.append(("required_skills", ", ".join(required_skills) if isinstance(required_skills, list) else str(required_skills)))
        if preferred_skills := data.get("preferred_skills", []):
            sections.append(("preferred_skills", ", ".join(preferred_skills) if isinstance(preferred_skills, list) else str(preferred_skills)))
        if responsibilities := data.get("responsibilities", []):
            sections.append(("responsibilities", "\n".join(responsibilities) if isinstance(responsibilities, list) else str(responsibilities)))

    return sections
