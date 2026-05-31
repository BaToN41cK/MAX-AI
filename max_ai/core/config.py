from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Config:
    def __init__(self) -> None:
        self.cohere_api_key = os.getenv("COHERE_API_KEY", "")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")
        self.cache_file: Optional[str] = os.getenv("MAX_AI_CACHE_FILE")
        self.history_file: Optional[str] = os.getenv("MAX_AI_HISTORY_FILE")

    def get_cohere_key(self, explicit_key: Optional[str] = None) -> str:
        return explicit_key or self.cohere_api_key

    def get_mistral_key(self, explicit_key: Optional[str] = None) -> str:
        return explicit_key or self.mistral_api_key

config = Config()
