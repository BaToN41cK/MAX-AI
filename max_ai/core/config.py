from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any
import yaml

script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", ".env")
load_dotenv(env_path)

DEFAULT_CONFIG = {
    "cohere_model": "command-a-03-2025",
    "mistral_model": "mistral-large-latest",
    "max_content_length": 50000,
    "summarize_threshold": 40000,
    "cache_ttl": 3600,
    "timeout": 30,
    "max_retries": 3,
    "rate_limit": 5,
    "system_prompt": "Ты — полезный ассистент.",
    "mistral_system_prompt": "Ты — опытный ассистент, который улучшает ответы."
}

class Config:
    def __init__(self) -> None:
        self.cohere_api_key = os.getenv("COHERE_API_KEY", "")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")
        self._config_file = os.path.join(script_dir, "..", "..", "max-ai.yaml")
        self._config: Dict[str, Any] = self._load_yaml_config()
        self.cache_file = self._resolve_path("MAX_AI_CACHE_FILE", "cache_file")
        self.history_file = self._resolve_path("MAX_AI_HISTORY_FILE", "history_file")
    
    def _resolve_path(self, env_var: str, yaml_key: str) -> Optional[str]:
        value = os.getenv(env_var, "") or self._config.get(yaml_key, "")
        if value:
            return os.path.expanduser(value)
        return None
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        return {**DEFAULT_CONFIG, **loaded}
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def get_cohere_key(self, explicit_key: Optional[str] = None) -> str:
        return explicit_key or self.cohere_api_key

    def get_mistral_key(self, explicit_key: Optional[str] = None) -> str:
        return explicit_key or self.mistral_api_key

config = Config()
