import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from click.testing import CliRunner
from max_ai.commands.run import run


def test_run_cli_without_urls(monkeypatch):
    class DummyAgent:
        def __init__(self, cohere_key=None, model=None):
            self.mistral_client = None

        def extract_urls(self, text):
            return []

        def run(self, query):
            return ("Dummy response", 0)

    monkeypatch.setattr('max_ai.commands.run.AIAgent', DummyAgent)
    runner = CliRunner()
    result = runner.invoke(run, ["тест"])

    assert result.exit_code == 0
    assert "Dummy response" in result.output
