import json
import logging
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from infrastructure.redis.client import RedisClient, redis_client

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class RedisCacheService:
    """Service to serialize, deserialize, and cache Pydantic domain models in Redis."""

    def __init__(
        self, client: Optional[RedisClient] = None, default_ttl_seconds: int = 3600
    ):
        """Initializes the Redis cache service.

        Args:
            client: Optional RedisClient instance. Defaults to global singleton.
            default_ttl_seconds: Default expiration time in seconds (default: 3600s / 1 hour).
        """
        self.client = client or redis_client
        self.default_ttl = default_ttl_seconds

    async def get_model(self, key: str, schema_cls: Type[T]) -> Optional[T]:
        """Retrieves and deserializes a Pydantic model from Redis cache.

        Args:
            key: Cache storage key.
            schema_cls: Target Pydantic model class.

        Returns:
            The instantiated domain model if found and valid, else None.
        """
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
        """Serializes and stores a Pydantic model in Redis cache.

        Args:
            key: Cache storage key.
            model_instance: Domain Pydantic model instance.
            ttl_seconds: Optional TTL override in seconds.

        Returns:
            True if cached successfully, False otherwise.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        try:
            raw_json = model_instance.model_dump_json()
            return await self.client.set(key, raw_json, ttl_seconds=ttl)
        except Exception as exc:
            logger.warning("Cache serialization failed for key %s: %s", key, str(exc))
            return False

    async def invalidate(self, key: str) -> bool:
        """Deletes a key from cache."""
        return await self.client.delete(key)
