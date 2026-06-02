from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any
import yaml

script_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
repo_root = os.path.abspath(os.path.join(src_root, '..'))

DEFAULT_CONFIG = {
    'cohere_model': 'command-a-03-2025',
    'mistral_model': 'mistral-large-latest',
    'max_content_length': 50000,
    'summarize_threshold': 40000,
    'cache_ttl': 3600,
    'timeout': 30,
    'max_retries': 3,
    'rate_limit': 5,
    'system_prompt': 'You are a helpful assistant.',
    'mistral_system_prompt': 'You are an experienced assistant that improves answers.',
    'cache_file': '~/.max_ai_cache.json',
    'history_file': '~/.max_ai_history.json',
}

ENV_PATHS = [
    os.path.join(os.getcwd(), 'config', '.env'),
    os.path.expanduser('~/.env'),
    os.path.join(repo_root, 'config', '.env'),
]

CONFIG_PATHS = [
    os.path.join(os.getcwd(), 'config', 'max-ai.yaml'),
    os.path.expanduser('~/.max-ai.yaml'),
    os.path.join(repo_root, 'config', 'max-ai.yaml'),
]


def _load_environment() -> None:
    for env_path in ENV_PATHS:
        if not env_path or not os.path.exists(env_path):
            continue
        try:
            load_dotenv(env_path, override=False)
        except (UnicodeDecodeError, OSError):
            # Skip invalid or unreadable environment files
            continue


class Config:
    def __init__(self, config_file: Optional[str] = None) -> None:
        self.verbose = False
        self._config_file = config_file
        self._load_environment()
        self.reload()

    def _load_environment(self) -> None:
        _load_environment()

    def reload(self) -> None:
        self._config = {**DEFAULT_CONFIG, **self._load_yaml_config()}
        self.cohere_api_key = os.getenv('COHERE_API_KEY', '')
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY', '')

    def set_config_file(self, config_file: Optional[str]) -> None:
        self._config_file = config_file
        self.reload()

    def _load_yaml_config(self) -> Dict[str, Any]:
        paths = [self._config_file] if self._config_file else CONFIG_PATHS
        for path in paths:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        loaded = yaml.safe_load(f)
                        if isinstance(loaded, dict):
                            return loaded
                except Exception:
                    pass
        return {}

    def _resolve_path(self, env_var: str, yaml_key: str, default: str) -> str:
        value = os.getenv(env_var, '') or self._config.get(yaml_key, '')
        if value:
            return os.path.expanduser(value)
        return os.path.expanduser(default)

    @property
    def cache_file(self) -> str:
        return self._resolve_path('MAX_AI_CACHE_FILE', 'cache_file', DEFAULT_CONFIG['cache_file'])

    @property
    def history_file(self) -> str:
        return self._resolve_path('MAX_AI_HISTORY_FILE', 'history_file', DEFAULT_CONFIG['history_file'])

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def get_cohere_key(self, explicit_key: Optional[str] = None) -> str:
        return explicit_key or self.cohere_api_key

    def get_mistral_key(self, explicit_key: Optional[str] = None) -> str:
        return explicit_key or self.mistral_api_key


config = Config()
