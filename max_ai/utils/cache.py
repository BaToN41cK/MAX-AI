import json
import os
from datetime import datetime
from max_ai.models.response import CacheEntry

CACHE_FILE = os.path.expanduser("~/.max_ai_cache.json")
HISTORY_FILE = os.path.expanduser("~/.max_ai_history.json")


class CacheManager:
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self._cache = {}
        self._load()

    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        response = v['response']
                        if response is None:
                            response = ''
                        self._cache[k] = CacheEntry(
                            query=v['query'],
                            response=response,
                            timestamp=datetime.fromisoformat(v['timestamp']),
                            ttl=v['ttl']
                        )
            except:
                self._cache = {}

    def _save(self):
        data = {k: {'query': v.query, 'response': v.response, 
                    'timestamp': v.timestamp.isoformat(), 'ttl': v.ttl}
                for k, v in self._cache.items()}
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

    def get(self, query: str) -> CacheEntry:
        if query in self._cache and not self._cache[query].is_expired():
            return self._cache[query]
        return None

    def set(self, query: str, response: str, ttl: int = 3600):
        self._cache[query] = CacheEntry(
            query=query, response=response,
            timestamp=datetime.now(), ttl=ttl
        )
        self._save()

    def clear(self):
        self._cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)