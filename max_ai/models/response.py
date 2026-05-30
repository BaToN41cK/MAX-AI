from dataclasses import dataclass, field
from datetime import datetime
import re

URL_PATTERN = re.compile(r'https?://[^/\s]+')

@dataclass
class AIResponse:
    content: str
    model: str
    timestamp: datetime
    cached: bool = False

    def __str__(self):
        return self.content


@dataclass
class CacheEntry:
    query: str
    response: str
    timestamp: datetime
    ttl: int

    def is_expired(self) -> bool:
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl


@dataclass
class HistoryEntry:
    query: str
    response: str
    timestamp: str
    model_used: str = "cohere"
    estimated_tokens: int = 0
    domains_visited: list = field(default_factory=list)
    
    def get_domains(self) -> list:
        return URL_PATTERN.findall(self.query) or []