import sys
import os
import types
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from max_ai.core.agent import AIAgent, PDFHandler, DocxHandler, HTMLHandler, YouTubeHandler


class TestAIAgent:
    def test_extract_urls_single(self):
        agent = AIAgent.__new__(AIAgent)
        agent.conversation_history = []
        urls = agent.extract_urls("Посмотри https://example.com")
        assert urls == ["https://example.com"]

    def test_extract_urls_multiple(self):
        agent = AIAgent.__new__(AIAgent)
        agent.conversation_history = []
        urls = agent.extract_urls("Смотри https://a.com и https://b.com")
        assert len(urls) == 2

    def test_extract_urls_none(self):
        agent = AIAgent.__new__(AIAgent)
        agent.conversation_history = []
        urls = agent.extract_urls("Привет, как дела?")
        assert urls == []


class TestHandlers:
    @pytest.mark.asyncio
    async def test_html_handler(self):
        handler = HTMLHandler()
        text, source = await handler.handle("<html><body><p>Привет</p></body></html>".encode('utf-8'), "https://example.com")
        assert "Привет" in text
        assert source == "web"

    @pytest.mark.asyncio
    async def test_pdf_handler_detects_pdf(self):
        handler = PDFHandler()
        assert await handler.can_handle("application/pdf", "test.pdf") is True
        assert await handler.can_handle("application/octet-stream", "test.pdf") is True

    @pytest.mark.asyncio
    async def test_docx_handler_detects_docx(self):
        handler = DocxHandler()
        assert await handler.can_handle("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "test.docx") is True

    def test_summarize_small_content(self):
        agent = AIAgent.__new__(AIAgent)
        agent.cohere_client = None
        agent.model_name = "command-a-03-2025"
        small_text = "Короткий текст"
        assert agent._summarize_content(small_text, "web") == small_text

    def test_summarize_triggers_on_large_content(self):
        agent = AIAgent.__new__(AIAgent)
        agent.cohere_client = None
        agent.model_name = "command-a-03-2025"
        large_text = "x" * 50000
        assert agent._summarize_content(large_text, "pdf") == large_text[:50000]

    def test_backoff_calculation(self):
        delays = []
        for attempt in range(3):
            delays.append(0.5 * (2 ** attempt))
        assert delays == [0.5, 1.0, 2.0]

    def test_url_validation(self):
        agent = AIAgent.__new__(AIAgent)
        agent.conversation_history = []
        urls = agent.extract_urls("Посмотри https://example.com")
        assert urls == ["https://example.com"]
        urls = agent.extract_urls("Невалидный: https://")
        assert "https://" not in urls or len(urls) == 0

    def test_extracts_youtube_url(self):
        agent = AIAgent.__new__(AIAgent)
        agent.conversation_history = []
        urls = agent.extract_urls("Смотри https://www.youtube.com/watch?v=K_ob1JBbd_g")
        assert urls == ["https://www.youtube.com/watch?v=K_ob1JBbd_g"]

    @pytest.mark.asyncio
    async def test_youtube_handler_html_fallback(self, monkeypatch):
        handler = YouTubeHandler()
        youtube_module = types.SimpleNamespace(
            YouTubeTranscriptApi=types.SimpleNamespace(
                get_transcript=lambda video_id: (_ for _ in ()).throw(Exception("transcript unavailable")),
                list_transcripts=lambda video_id: types.SimpleNamespace(
                    find_transcript=lambda langs: (_ for _ in ()).throw(Exception("transcript unavailable"))
                )
            )
        )
        monkeypatch.setitem(sys.modules, 'youtube_transcript_api', youtube_module)

        html = (
            '<html><head><title>Test Video</title>'
            '<meta name="description" content="Sample description for video." />'
            '</head><body></body></html>'
        )
        text, source = await handler.handle(html.encode('utf-8'), "https://www.youtube.com/watch?v=K_ob1JBbd_g")
        assert "Test Video" in text
        assert "Sample description for video." in text
        assert source == 'youtube'