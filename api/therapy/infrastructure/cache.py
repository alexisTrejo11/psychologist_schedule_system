from django.core.cache import cache

class CacheManager:
    CACHE_PREFIX = "therapy_session_"
    CACHE_TIMEOUT = 60 * 15  # 15 mins

    def get_cache_key(self, session_id: int) -> str:
        """Generates a unique key for the cache."""
        return f"{self.CACHE_PREFIX}{session_id}"

    def get(self, key: str):
        """Retrieves a value from the cache."""
        return cache.get(key)

    def set(self, key: str, value, timeout: int = None):
        """Stores a value in the cache."""
        cache.set(key, value, timeout or self.CACHE_TIMEOUT)

    def delete(self, key: str):
        """Deletes a value from the cache."""
        cache.delete(key)

    def generate_search_key(self, filters: dict) -> str:
        """Generates a unique key for searches based on filters."""
        return f"search_{hash(frozenset(filters.items()))}"
