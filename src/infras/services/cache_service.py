import json
import time
from typing import Any, Optional
import redis.asyncio as aioredis

from src.app.services.cache_service import CacheService
from src.core.logger import setup_app_level_logger

logger = setup_app_level_logger(__name__)


class InMemoryCacheService(CacheService):
    """
    In-memory implementation of CacheService.
    Ideal for testing, development, or fallback when Redis is unavailable.
    """

    def __init__(self):
        # Store tuple: (value, expire_timestamp_or_none)
        self._cache: dict[str, tuple[Any, Optional[float]]] = {}

    async def get(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if item is None:
            return None
        value, expire_at = item
        if expire_at is not None and time.time() > expire_at:
            del self._cache[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        expire_at = time.time() + ttl if ttl is not None else None
        self._cache[key] = (value, expire_at)
        return True

    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def clear_prefix(self, prefix: str) -> int:
        keys_to_del = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_del:
            del self._cache[k]
        return len(keys_to_del)

    def clear_all(self):
        """Helper to clear whole in-memory cache during tests."""
        self._cache.clear()


class RedisCacheService(CacheService):
    """
    Redis implementation of CacheService using redis-py async client.
    Includes serialization and graceful failure handling.
    """

    def __init__(self, redis_url: str, default_ttl: int = 60):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._client: Optional[aioredis.Redis] = None

    def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2.0,
            )
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = self._get_client()
            raw_value = await client.get(key)
            if raw_value is None:
                return None
            return json.loads(raw_value)
        except Exception as e:
            logger.warning(f"Redis get failed for key '{key}': {e}. Returning None.")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            client = self._get_client()
            effective_ttl = ttl if ttl is not None else self.default_ttl
            serialized = json.dumps(value, default=str)
            await client.set(key, serialized, ex=effective_ttl)
            return True
        except Exception as e:
            logger.warning(f"Redis set failed for key '{key}': {e}.")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = self._get_client()
            result = await client.delete(key)
            return bool(result)
        except Exception as e:
            logger.warning(f"Redis delete failed for key '{key}': {e}.")
            return False

    async def clear_prefix(self, prefix: str) -> int:
        try:
            client = self._get_client()
            keys = []
            async for k in client.scan_iter(match=f"{prefix}*"):
                keys.append(k)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis clear_prefix failed for pattern '{prefix}*': {e}.")
            return 0
