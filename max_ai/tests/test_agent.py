import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from max_ai.core.agent import AIAgent, PDFHandler, DocxHandler, HTMLHandler


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