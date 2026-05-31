import json
import os
from datetime import datetime
from typing import Optional
from max_ai.models.response import CacheEntry
from max_ai.constants import MAX_CONTENT_LENGTH

DEFAULT_CACHE_FILE = os.path.expanduser("~/.max_ai_cache.json")


class CacheManager:
    def __init__(self, cache_file: str = DEFAULT_CACHE_FILE) -> None:
        self.cache_file = cache_file
        self._cache: dict[str, CacheEntry] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    response = v.get('response') or ""
                    self._cache[k] = CacheEntry(
                        query=v['query'],
                        response=response,
                        timestamp=datetime.fromisoformat(v['timestamp']),
                        ttl=v['ttl']
                    )
        except (json.JSONDecodeError, KeyError, ValueError):
            self._cache = {}

    def _save(self) -> None:
        data = {
            k: {
                'query': v.query,
                'response': v.response,
                'timestamp': v.timestamp.isoformat(),
                'ttl': v.ttl
            }
            for k, v in self._cache.items()
        }
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def get(self, query: str) -> Optional[CacheEntry]:
        if query in self._cache and not self._cache[query].is_expired():
            return self._cache[query]
        return None

    def set(self, query: str, response: str, ttl: int = 3600) -> None:
        self._cache[query] = CacheEntry(
            query=query,
            response=response,
            timestamp=datetime.now(),
            ttl=ttl
        )
        self._save()

    def clear(self) -> None:
        self._cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
