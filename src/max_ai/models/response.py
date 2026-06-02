from dataclasses import dataclass, field
from datetime import datetime
from max_ai.constants import DOMAIN_PATTERN

@dataclass
class AIResponse:
    content: str
    model: str
    timestamp: datetime
    cached: bool = False

    def __str__(self) -> str:
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
    domains_visited: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    source_types: list[str] = field(default_factory=list)

    def get_domains(self) -> list[str]:
        return DOMAIN_PATTERN.findall(self.query) or []
