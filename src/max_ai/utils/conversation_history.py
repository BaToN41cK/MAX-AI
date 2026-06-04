import json
import os
from typing import List, Optional
from datetime import datetime


class ConversationHistory:
    def __init__(self, history_file: str = None):
        if history_file is None:
            history_file = os.path.expanduser("~/.max_ai_conversation_history.json")
        self.history_file = history_file
        self._history: List[dict] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.history_file):
            return
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self._history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._history = []

    def _save(self) -> None:
        parent_dir = os.path.dirname(self.history_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self._history, f, ensure_ascii=False, indent=2)

    def add_conversation(self, user_input: str, bot_response: str) -> None:
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response
        }
        self._history.append(conversation)
        if len(self._history) > 5:
            self._history.pop(0)
        self._save()

    def get_last_conversations(self, limit: int = 5) -> List[dict]:
        return self._history[-limit:] if self._history else []

    def clear_history(self) -> None:
        self._history = []
        self._save()