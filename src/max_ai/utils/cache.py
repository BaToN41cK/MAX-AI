import json
import os
import sqlite3
from datetime import datetime
from typing import Optional
from max_ai.models.response import CacheEntry
import cachetools

DEFAULT_CACHE_FILE = os.path.expanduser("~/.max_ai_cache.json")


class CacheManager:
    def __init__(self, cache_file: str = DEFAULT_CACHE_FILE, use_sqlite: Optional[bool] = None) -> None:
        self.cache_file = os.path.expanduser(cache_file)
        self._cache: dict[str, CacheEntry] = {}
        self._use_sqlite = self._determine_sqlite(use_sqlite)
        self._conn: Optional[sqlite3.Connection] = None
        if self._use_sqlite:
            self._connect_db()
        else:
            self._load()

    def _determine_sqlite(self, use_sqlite: Optional[bool]) -> bool:
        if use_sqlite is not None:
            return use_sqlite
        return self.cache_file.lower().endswith('.db')

    def _connect_db(self) -> None:
        parent_dir = os.path.dirname(self.cache_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        self._conn = sqlite3.connect(self.cache_file, timeout=30)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS cache (query TEXT PRIMARY KEY, response TEXT, timestamp TEXT, ttl INTEGER)"
        )
        self._conn.commit()

    def _load(self) -> None:
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    self._cache[k] = CacheEntry(
                        query=v['query'],
                        response=v.get('response', ''),
                        timestamp=datetime.fromisoformat(v['timestamp']),
                        ttl=v['ttl']
                    )
        except (json.JSONDecodeError, KeyError, ValueError):
            self._cache = {}

    def _save(self) -> None:
        if self._use_sqlite:
            return
        data = {
            k: {
                'query': v.query,
                'response': v.response,
                'timestamp': v.timestamp.isoformat(),
                'ttl': v.ttl,
            }
                for k, v in self._cache.items()
        }
        parent_dir = os.path.dirname(self.cache_file)
        if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, query: str) -> Optional[CacheEntry]:
        if self._use_sqlite and self._conn is not None:
            cursor = self._conn.execute(
                "SELECT response, timestamp, ttl FROM cache WHERE query = ?",
                (query,)
            )
            row = cursor.fetchone()
            if row:
                response, timestamp, ttl = row
                entry = CacheEntry(
                    query=query,
                    response=response,
                    timestamp=datetime.fromisoformat(timestamp),
                    ttl=ttl,
                )
                if not entry.is_expired():
                    return entry
                self._conn.execute("DELETE FROM cache WHERE query = ?", (query,))
                self._conn.commit()
            return None

        if query in self._cache and not self._cache[query].is_expired():
            return self._cache[query]
        return None

    def set(self, query: str, response: str, ttl: int = 3600) -> None:
        entry = CacheEntry(
            query=query,
            response=response,
            timestamp=datetime.now(),
            ttl=ttl,
        )
        if self._use_sqlite and self._conn is not None:
            self._conn.execute(
                "INSERT OR REPLACE INTO cache (query, response, timestamp, ttl) VALUES (?, ?, ?, ?)",
                (entry.query, entry.response, entry.timestamp.isoformat(), entry.ttl),
            )
            self._conn.commit()
            return

        self._cache[query] = entry
        self._save()

    def clear(self) -> None:
        if self._use_sqlite and self._conn is not None:
            self._conn.execute("DELETE FROM cache")
            self._conn.commit()
            return

        self._cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)