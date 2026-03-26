from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheService(ABC):
    """
    Abstract Cache Service interface (Port in Clean Architecture).
    Decouples application use cases and controllers from specific caching technologies (e.g. Redis, Memcached, In-Memory).
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve an item from the cache.
        Returns None if key does not exist or has expired.
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store an item in the cache with an optional Time-To-Live (seconds).
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Remove an item from the cache.
        Returns True if deleted, False otherwise.
        """
        pass

    @abstractmethod
    async def clear_prefix(self, prefix: str) -> int:
        """
        Remove all keys starting with the given prefix.
        Returns the number of keys removed.
        """
        pass
