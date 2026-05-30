import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re
from max_ai.models.response import HistoryEntry

HISTORY_FILE = os.path.expanduser("~/.max_ai_history.json")
URL_PATTERN = re.compile(r'https?://[^/\s]+')


class HistoryManager:
    def __init__(self, history_file: str = HISTORY_FILE, max_entries: int = 100):
        self.history_file = history_file
        self.max_entries = max_entries
        self._entries = []
        self._load()

    def _load(self):
        if os.path.exists(self.history_file):
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
            except:
                self._entries = []

    def _save(self):
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

    def add(self, query: str, response: str, model_used: str = "cohere", tokens: int = 0):
        domains = list(set(URL_PATTERN.findall(query)))
        
        self._entries.append(HistoryEntry(
            query=query,
            response=response,
            timestamp=datetime.now().isoformat(),
            model_used=model_used,
            estimated_tokens=tokens,
            domains_visited=domains
        ))
        self._save()

    def get(self, limit: int = 10) -> list:
        return [e.__dict__ for e in self._entries[-limit:]]

    def clear(self):
        self._entries = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

    def get_stats(self, days: int = 7) -> dict:
        now = datetime.now()
        cutoff = now - timedelta(days=days)
        
        total_requests = 0
        total_tokens = 0
        model_counts = defaultdict(int)
        domain_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for entry in self._entries:
            try:
                entry_time = datetime.fromisoformat(entry.timestamp)
                if entry_time >= cutoff:
                    total_requests += 1
                    total_tokens += entry.estimated_tokens
                    model_counts[entry.model_used] += 1
                    for domain in entry.domains_visited:
                        domain_counts[domain] += 1
                    daily_key = entry_time.strftime('%Y-%m-%d')
                    daily_counts[daily_key] += 1
            except:
                continue

        # Approximate cost: Cohere ~$0.001 per 1k tokens, Mistral ~$0.002
        cost_estimate = (total_tokens / 1000) * 0.001  # Simplified
        
        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'cost_estimate_usd': cost_estimate,
            'model_usage': dict(model_counts),
            'top_domains': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'daily_breakdown': dict(sorted(daily_counts.items()))
        }