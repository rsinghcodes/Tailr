import json
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from infrastructure.redis.client import RedisClient, redis_client

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class RedisCacheService:
    """Service to serialize, deserialize, and cache Pydantic domain models in Redis."""

    def __init__(self, client: Optional[RedisClient] = None, default_ttl_seconds: int = 3600):
        self.client = client or redis_client
        self.default_ttl = default_ttl_seconds

    async def get_model(self, key: str, schema_cls: Type[T]) -> Optional[T]:
        raw_json = await self.client.get(key)
        if not raw_json:
            return None

        try:
            data = json.loads(raw_json)
            return schema_cls.model_validate(data)
        except Exception as exc:
            logger.warning("Cache deserialization failed for key %s: %s", key, str(exc))
            return None

    async def set_model(
        self, key: str, model_instance: BaseModel, ttl_seconds: Optional[int] = None
    ) -> bool:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        try:
            raw_json = model_instance.model_dump_json()
            return await self.client.set(key, raw_json, ttl_seconds=ttl)
        except Exception as exc:
            logger.warning("Cache serialization failed for key %s: %s", key, str(exc))
            return False

    async def get(self, key: str, schema_cls: Type[T]) -> Optional[T]:
        return await self.get_model(key, schema_cls)

    async def set(self, key: str, model_instance: BaseModel, ttl_seconds: Optional[int] = None) -> bool:
        return await self.set_model(key, model_instance, ttl_seconds)

    async def invalidate(self, key: str) -> bool:
        return await self.client.delete(key)


_redis_cache_singleton = RedisCacheService()


def get_redis_cache_service() -> RedisCacheService:
    return _redis_cache_singleton
