from django.core.cache import cache
from typing import Dict, List, Any

class CacheManager:
    def __init__(self, cache_prefix):
        self.cache_prefix = cache_prefix

    CACHE_TIMEOUT = 60 * 15  # 15 mins

    def get_cache_key(self, id: int) -> str:
        return f"{self.cache_prefix}{id}"

    def get(self, key: str) -> Any:
        return cache.get(key)

    def set(self, key: str, value: Any, timeout: int = None):
        cache.set(key, value, timeout or self.CACHE_TIMEOUT)

    def set_multi(self, data: Dict[str, Any], timeout: int = None):
        cache.set_many(data, timeout or self.CACHE_TIMEOUT)

    def delete(self, key: str):
        cache.delete(key)

    def delete_multi(self, keys: List[str]):
        cache.delete_many(keys)

    def generate_search_key(self, filters: dict) -> str:
        return f"search_{hash(frozenset(filters.items()))}"