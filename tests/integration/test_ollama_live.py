import pytest
import httpx
from config.settings import settings
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.ollama.embedding_provider import OllamaEmbeddingProvider


async def get_available_models() -> list[str]:
    """Helper to query local Ollama tags API for pulled models."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
    return []


@pytest.mark.asyncio
async def test_ollama_live_generation():
    models = await get_available_models()
    if not models:
        pytest.skip("Ollama service is offline or has no models pulled.")
    
    # Pick the first available model
    test_model = models[0]
    provider = OllamaProvider(default_model=test_model)
    try:
        response = await provider.generate("Say only the word 'OK'.")
        assert len(response) > 0
    finally:
        await provider.close()


@pytest.mark.asyncio
async def test_ollama_live_embedding():
    models = await get_available_models()
    if not models:
        pytest.skip("Ollama service is offline or has no models pulled.")
    
    # Prefer a model containing 'embed', fallback to the first available model
    embed_models = [m for m in models if "embed" in m]
    test_model = embed_models[0] if embed_models else models[0]
    
    provider = OllamaEmbeddingProvider(default_model=test_model)
    try:
        embedding = await provider.generate_embedding("Hello world")
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert isinstance(embedding[0], float)
    finally:
        await provider.close()
