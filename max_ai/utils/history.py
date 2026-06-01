import json
import os
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict
from max_ai.models.response import HistoryEntry
from max_ai.constants import DOMAIN_PATTERN

DEFAULT_HISTORY_FILE = os.path.expanduser("~/.max_ai_history.json")


class HistoryManager:
    def __init__(self, history_file: str = DEFAULT_HISTORY_FILE, max_entries: int = 100) -> None:
        self.history_file = os.path.expanduser(history_file)
        self.max_entries = max_entries
        self._entries: list[HistoryEntry] = []
        self._use_sqlite = self.history_file.lower().endswith('.db')
        self._conn: Optional[sqlite3.Connection] = None
        if self._use_sqlite:
            self._connect_db()
        else:
            self._load()

    def _connect_db(self) -> None:
        parent_dir = os.path.dirname(self.history_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        self._conn = sqlite3.connect(self.history_file, timeout=30)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS history ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "query TEXT, response TEXT, timestamp TEXT, "
            "model_used TEXT, estimated_tokens INTEGER, domains_visited TEXT)"
        )
        self._conn.commit()

    def _load(self) -> None:
        if not os.path.exists(self.history_file):
            return
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for e in data:
                    self._entries.append(HistoryEntry(
                        query=e.get('query', ''),
                        response=e.get('response', ''),
                        timestamp=e.get('timestamp', datetime.now().isoformat()),
                        model_used=e.get('model_used', 'cohere'),
                        estimated_tokens=e.get('estimated_tokens', 0),
                        domains_visited=e.get('domains_visited', [])
                    ))
        except (json.JSONDecodeError, KeyError, ValueError):
            self._entries = []

    def _save(self) -> None:
        if self._use_sqlite:
            return
        data = [{
            'query': e.query,
            'response': e.response,
            'timestamp': e.timestamp,
            'model_used': e.model_used,
            'estimated_tokens': e.estimated_tokens,
            'domains_visited': e.domains_visited
        } for e in self._entries]
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data[-self.max_entries:], f, ensure_ascii=False, indent=2)

    def _row_to_entry(self, row: tuple) -> HistoryEntry:
        query, response, timestamp, model_used, estimated_tokens, domains_json = row
        domains = json.loads(domains_json or '[]')
        return HistoryEntry(
            query=query,
            response=response,
            timestamp=timestamp,
            model_used=model_used,
            estimated_tokens=estimated_tokens,
            domains_visited=domains
        )

    def add(self, query: str, response: str, model_used: str = "cohere", tokens: int = 0) -> None:
        domains = list(set(DOMAIN_PATTERN.findall(query)))
        timestamp = datetime.now().isoformat()

        if self._use_sqlite and self._conn is not None:
            self._conn.execute(
                "INSERT INTO history (query, response, timestamp, model_used, estimated_tokens, domains_visited) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (query, response, timestamp, model_used, tokens, json.dumps(domains, ensure_ascii=False))
            )
            self._conn.commit()
            return

        self._entries.append(HistoryEntry(
            query=query,
            response=response,
            timestamp=timestamp,
            model_used=model_used,
            estimated_tokens=tokens,
            domains_visited=domains
        ))
        self._save()

    def get(self, limit: int = 10) -> List[dict]:
        if self._use_sqlite and self._conn is not None:
            cursor = self._conn.execute(
                "SELECT query, response, timestamp, model_used, estimated_tokens, domains_visited "
                "FROM history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return [self._row_to_entry(row).__dict__ for row in cursor.fetchall()]

        return [e.__dict__ for e in self._entries[-limit:]]

    def clear(self) -> None:
        if self._use_sqlite and self._conn is not None:
            self._conn.execute("DELETE FROM history")
            self._conn.commit()
            return

        self._entries = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

    def get_stats(self, days: int = 7) -> Dict:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        total_requests = 0
        total_tokens = 0
        model_counts: Dict[str, int] = defaultdict(int)
        domain_counts: Dict[str, int] = defaultdict(int)
        daily_counts: Dict[str, int] = defaultdict(int)

        if self._use_sqlite and self._conn is not None:
            cursor = self._conn.execute(
                "SELECT query, response, timestamp, model_used, estimated_tokens, domains_visited "
                "FROM history WHERE timestamp >= ?",
                (cutoff,)
            )
            rows = [self._row_to_entry(row) for row in cursor.fetchall()]
        else:
            rows = []
            for entry in self._entries:
                try:
                    if datetime.fromisoformat(entry.timestamp) >= datetime.fromisoformat(cutoff):
                        rows.append(entry)
                except (ValueError, TypeError):
                    continue

        for entry in rows:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp)
                total_requests += 1
                total_tokens += entry.estimated_tokens
                model_counts[entry.model_used] += 1
                for domain in entry.domains_visited:
                    domain_counts[domain] += 1
                daily_key = entry_time.strftime('%Y-%m-%d')
                daily_counts[daily_key] += 1
            except (ValueError, TypeError):
                continue

        cost_estimate = (total_tokens / 1000) * 0.001
        unique_domains = len(domain_counts)
        avg_tokens = total_tokens / total_requests if total_requests else 0.0

        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'average_tokens': avg_tokens,
            'unique_domains': unique_domains,
            'cost_estimate_usd': cost_estimate,
            'model_usage': dict(model_counts),
            'top_domains': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'daily_breakdown': dict(sorted(daily_counts.items()))
        }
