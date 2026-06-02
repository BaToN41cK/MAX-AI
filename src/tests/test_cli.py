from click.testing import CliRunner
from max_ai.commands import run as run_cmd
from max_ai.commands import cache as cache_cmd
from max_ai.commands import history as history_cmd
from max_ai.commands import status as status_cmd
from max_ai.core import config
from max_ai.utils.history import HistoryManager
import os


def test_run_shows_source_tags_and_response(monkeypatch, tmp_path):
    class DummyAgent:
        def __init__(self, cohere_key=None, model=None):
            self.mistral_client = None
        def extract_urls(self, text):
            return ["http://example.com/doc.pdf", "https://youtube.com/watch?v=abc"]
        def run(self, query):
            return ("Тестовый ответ", 5)

    monkeypatch.setattr(run_cmd, 'AIAgent', DummyAgent)
    # ensure cache/history use temp files
    config.cache_file = str(tmp_path / "cache.json")
    config.history_file = str(tmp_path / "history.json")

    runner = CliRunner()
    result = runner.invoke(run_cmd.run, ["http://example.com/doc.pdf", "https://youtube.com/watch?v=abc"])
    assert result.exit_code == 0
    assert "doc.pdf" in result.output
    assert "YOUTUBE" in result.output or "YOUTUBE".lower() in result.output.lower()
    assert "Тестовый ответ" in result.output


def test_cache_clear_outputs_message(runner=None):
    runner = runner or CliRunner()
    result = runner.invoke(cache_cmd.cache_clear)
    assert result.exit_code == 0
    assert "Кеш успешно очищен" in result.output


def test_status_reads_history_and_outputs_summary(tmp_path, monkeypatch):
    # point config to a temp history file and populate it
    hist_file = tmp_path / "history.json"
    config.history_file = str(hist_file)
    hist = HistoryManager(str(hist_file))
    hist.add("привет", "ответ", model_used="cohere", tokens=10)

    runner = CliRunner()
    result = runner.invoke(status_cmd.status, [])
    assert result.exit_code == 0
    assert "Total Requests" in result.output or "Total Requests".lower() in result.output.lower()
    assert "1" in result.output
