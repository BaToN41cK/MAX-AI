from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        self.cohere_api_key = os.getenv("COHERE_API_KEY", "")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")

    def get_cohere_key(self, explicit_key: str = None) -> str:
        return explicit_key or self.cohere_api_key

    def get_mistral_key(self, explicit_key: str = None) -> str:
        return explicit_key or self.mistral_api_key

config = Config()