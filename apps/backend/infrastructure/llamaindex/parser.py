import logging
from typing import Optional
from llama_cloud import AsyncLlamaCloud
from config.settings import settings

logger = logging.getLogger(__name__)


class LlamaDocParser:
    """PDF/DOCX parser using LlamaCloud parsing API."""

    def __init__(self, client: Optional[AsyncLlamaCloud] = None):
        self._client = client or AsyncLlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)

    async def parse_file(self, file_path: str) -> list[dict]:
        with open(file_path, "rb") as f:
            response = await self._client.parsing.parse(
                upload_file=f,
                tier="fast",
                version="latest",
                expand=["markdown", "text"],
            )
        markdown = self._extract_text(response)
        if markdown:
            return [{"text": markdown, "metadata": {"source": file_path}}]
        return []

    async def parse_bytes(self, file_bytes: bytes, filename: str) -> list[dict]:
        import io
        response = await self._client.parsing.parse(
            upload_file=(filename, io.BytesIO(file_bytes)),
            tier="fast",
            version="latest",
            expand=["markdown", "text"],
        )
        markdown = self._extract_text(response)
        if markdown:
            return [{"text": markdown, "metadata": {"source": filename}}]
        return []

    @staticmethod
    def _extract_text(response) -> str:
        markdown = getattr(response, "markdown", None)
        if markdown and hasattr(markdown, "pages"):
            parts = [p.markdown for p in markdown.pages if getattr(p, "markdown", None)]
            if parts:
                return "\n\n".join(parts)
        text = getattr(response, "text", None)
        if text and hasattr(text, "pages"):
            parts = [p.text for p in text.pages if getattr(p, "text", None)]
            if parts:
                return "\n\n".join(parts)
        return ""
