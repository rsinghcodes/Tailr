import logging
from typing import Optional
from llama_cloud import AsyncLlamaCloud
from config.settings import settings

logger = logging.getLogger(__name__)

PIPELINE_NAME = settings.LLAMA_CLOUD_PIPELINE_NAME


class LlamaIndexService:
    """Vector store operations via LlamaCloud Pipelines API."""

    def __init__(self, client: Optional[AsyncLlamaCloud] = None):
        self._client = client or AsyncLlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)
        self._pipeline_id: str | None = None

    async def _get_pipeline_id(self) -> str:
        if self._pipeline_id is None:
            pipelines = self._client.pipelines
            resp = await pipelines.list(pipeline_name=PIPELINE_NAME)
            items = getattr(resp, "pipelines", resp) if hasattr(resp, "pipelines") else resp
            for p in items:
                if getattr(p, "name", None) == PIPELINE_NAME:
                    self._pipeline_id = str(p.id)
                    break
            if self._pipeline_id is None:
                raise RuntimeError(f"LlamaCloud pipeline '{PIPELINE_NAME}' not found")
        return self._pipeline_id

    async def query_context(self, query: str, top_k: int = 5) -> str:
        try:
            pipeline_id = await self._get_pipeline_id()
            result = await self._client.pipelines.retrieve(
                pipeline_id=pipeline_id,
                query=query,
                dense_similarity_top_k=top_k,
            )
            nodes = getattr(result, "nodes", result) if hasattr(result, "nodes") else []
            if not nodes:
                return "No relevant context found."
            parts = []
            for node in nodes:
                score = getattr(node, "score", 0) or 0
                text = getattr(node, "text", "") or getattr(node, "node", {}).get("text", "")
                parts.append(f"[score: {score:.2f}] {text}")
            return "\n\n".join(parts)
        except Exception as exc:
            logger.error("LlamaCloud retrieval failed: %s", str(exc))
            return "No relevant context found."
