"""Constants for MAX-AI."""

import re

URL_PATTERN = re.compile(r'https?://\S+')
DOMAIN_PATTERN = re.compile(r'https?://[^/\s]+')

MAX_CONTENT_LENGTH = 50000

DEFAULT_MAX_CONTENT_LENGTH = 50000
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
DEFAULT_CACHE_TTL = 3600

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

COHERE_MODEL = "command-a-03-2025"
MISTRAL_MODEL = "mistral-large-latest"

CACHE_FILE = "~/.max_ai_cache.json"
HISTORY_FILE = "~/.max_ai_history.json"