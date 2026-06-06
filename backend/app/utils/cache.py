import time
from typing import Any, Dict, Tuple

class InMemoryCache:
    def __init__(self):
        # Maps cache_key -> (value, expiry_timestamp)
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """Retrieves a value from cache if it exists and has not expired."""
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            return None
        return val

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Sets a value in the cache with a TTL (Time To Live)."""
        expiry = time.time() + ttl_seconds
        self._store[key] = (value, expiry)

    def invalidate(self, key: str) -> None:
        """Removes a key from cache."""
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        """Clears all cached items."""
        self._store.clear()

# Global cache instance
cache_store = InMemoryCache()
