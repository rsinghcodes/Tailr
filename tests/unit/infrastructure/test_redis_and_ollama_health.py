import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import BaseModel
from infrastructure.redis.client import RedisClient
from infrastructure.redis.cache import RedisCacheService
from infrastructure.ollama.health import OllamaHealthChecker


class SampleModel(BaseModel):
    id: str
    name: str


@pytest.mark.asyncio
async def test_redis_client_ping_and_operations():
    client = RedisClient(redis_url="redis://localhost:6379/0")
    
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.get.return_value = '{"id": "1", "name": "Test"}'
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True

    with patch.object(client, "get_client", return_value=mock_redis):
        assert await client.ping() is True
        
        # Test Cache Service
        cache = RedisCacheService(client=client)
        
        # Test get_model
        model = await cache.get_model("test_key", SampleModel)
        assert model is not None
        assert model.id == "1"
        assert model.name == "Test"
        
        # Test set_model
        obj = SampleModel(id="2", name="Sample")
        cached_set = await cache.set_model("test_key", obj)
        assert cached_set is True


@pytest.mark.asyncio
async def test_ollama_health_checker_healthy():
    checker = OllamaHealthChecker(base_url="http://localhost:11434")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "qwen3:8b"},
            {"name": "nomic-embed-text"}
        ]
    }
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        res = await checker.check_health()
        assert res["online"] is True
        assert res["status"] == "healthy"
        assert "qwen3:8b" in res["available_models"]


@pytest.mark.asyncio
async def test_ollama_health_checker_offline():
    checker = OllamaHealthChecker(base_url="http://localhost:11434")
    
    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection refused")):
        res = await checker.check_health()
        assert res["online"] is False
        assert res["status"] == "offline"
        assert res["error"] == "Connection refused"
