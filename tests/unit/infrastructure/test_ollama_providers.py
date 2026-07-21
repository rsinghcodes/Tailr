import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
from pydantic import BaseModel
from infrastructure.ollama.llm_provider import OllamaProvider
from infrastructure.ollama.embedding_provider import OllamaEmbeddingProvider
from domain.shared.exceptions import LLMProviderTimeoutError, LLMValidationError


class DummySchema(BaseModel):
    name: str
    age: int


@pytest.mark.asyncio
async def test_ollama_provider_generate_text():
    provider = OllamaProvider(base_url="http://localhost:11434")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {"role": "assistant", "content": "Hello world"}
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await provider.generate("test prompt")
        assert result == "Hello world"
        mock_post.assert_called_once()
        
        # Verify request structure
        called_args = mock_post.call_args[1]
        assert called_args["json"]["model"] == "qwen2.5:7b-instruct"
        assert called_args["json"]["messages"] == [{"role": "user", "content": "test prompt"}]
    
    await provider.close()


@pytest.mark.asyncio
async def test_ollama_provider_generate_structured():
    provider = OllamaProvider(base_url="http://localhost:11434")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {"role": "assistant", "content": '{"name": "Alice", "age": 30}'}
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await provider.generate("test prompt", schema=DummySchema)
        assert isinstance(result, DummySchema)
        assert result.name == "Alice"
        assert result.age == 30
    
    await provider.close()


@pytest.mark.asyncio
async def test_ollama_provider_timeout():
    provider = OllamaProvider(base_url="http://localhost:11434")
    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("timeout")
        with pytest.raises(LLMProviderTimeoutError):
            await provider.generate("test prompt")
    await provider.close()


@pytest.mark.asyncio
async def test_ollama_provider_validation_error():
    provider = OllamaProvider(base_url="http://localhost:11434")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {"role": "assistant", "content": '{"name": "Alice", "age": "not-an-int"}'}
    }
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(LLMValidationError):
            await provider.generate("test prompt", schema=DummySchema)
    await provider.close()


@pytest.mark.asyncio
async def test_ollama_embedding_provider():
    provider = OllamaEmbeddingProvider(base_url="http://localhost:11434")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await provider.generate_embedding("hello")
        assert res == [0.1, 0.2, 0.3]
    await provider.close()


@pytest.mark.asyncio
async def test_ollama_embeddings_batch():
    provider = OllamaEmbeddingProvider(base_url="http://localhost:11434")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
    mock_response.raise_for_status = MagicMock()
    
    with patch.object(provider.client, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await provider.generate_embeddings(["hello", "world"])
        assert res == [[0.1, 0.2], [0.3, 0.4]]
    await provider.close()
