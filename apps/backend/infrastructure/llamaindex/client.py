import logging
from llama_cloud import AsyncLlamaCloud
from config.settings import settings

logger = logging.getLogger(__name__)

_llama_client: AsyncLlamaCloud | None = None


def get_llama_client() -> AsyncLlamaCloud:
    global _llama_client
    if _llama_client is None:
        _llama_client = AsyncLlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)
    return _llama_client
