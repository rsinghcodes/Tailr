import logging
from typing import Optional
import redis.asyncio as redis
from config.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client wrapper providing connection pooling and health checks."""

    def __init__(self, redis_url: Optional[str] = None):
        """Initializes the Redis client.

        Args:
            redis_url: Optional Redis connection URL. Defaults to settings.REDIS_URL.
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None

    def get_client(self) -> redis.Redis:
        """Returns or initializes the async Redis client instance."""
        if self._client is None:
            self._pool = redis.ConnectionPool.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=3.0,
                socket_timeout=3.0,
            )
            self._client = redis.Redis(connection_pool=self._pool)
        return self._client

    async def ping(self) -> bool:
        """Pings the Redis server to verify connectivity.

        Returns:
            True if Redis responds to PING, False otherwise.
        """
        try:
            client = self.get_client()
            response = await client.ping()
            return response is True or response == "PONG"
        except Exception as exc:
            logger.warning("Redis ping failed at %s: %s", self.redis_url, str(exc))
            return False

    async def get(self, key: str) -> Optional[str]:
        """Gets string value by key."""
        try:
            client = self.get_client()
            return await client.get(key)
        except Exception as exc:
            logger.warning("Redis GET error for key %s: %s", key, str(exc))
            return None

    async def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
        """Sets key-value pair with optional TTL."""
        try:
            client = self.get_client()
            if ttl_seconds:
                await client.set(key, value, ex=ttl_seconds)
            else:
                await client.set(key, value)
            return True
        except Exception as exc:
            logger.warning("Redis SET error for key %s: %s", key, str(exc))
            return False

    async def delete(self, key: str) -> bool:
        """Deletes key from Redis."""
        try:
            client = self.get_client()
            await client.delete(key)
            return True
        except Exception as exc:
            logger.warning("Redis DELETE error for key %s: %s", key, str(exc))
            return False

    async def close(self) -> None:
        """Closes the Redis connection pool."""
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.aclose()
            self._pool = None


redis_client = RedisClient()
