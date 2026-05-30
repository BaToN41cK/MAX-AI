import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import cohere
from .config import config
import PyPDF2
import docx
import io
import urllib.parse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None


class BaseHandler:
    async def can_handle(self, content_type: str, url: str) -> bool:
        return False

    async def handle(self, content: bytes, url: str) -> str:
        return None


class PDFHandler(BaseHandler):
    async def can_handle(self, content_type: str, url: str) -> bool:
        return 'application/pdf' in content_type or url.lower().endswith('.pdf')

    async def handle(self, content: bytes, url: str) -> tuple:
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text[:50000], 'pdf'  # ограничиваем длину
        except Exception as e:
            return f"Ошибка обработки PDF {url}: {str(e)}", 'error'


class DocxHandler(BaseHandler):
    async def can_handle(self, content_type: str, url: str) -> bool:
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or url.lower().endswith('.docx')

    async def handle(self, content: bytes, url: str) -> tuple:
        try:
            doc = docx.Document(io.BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text[:50000], 'docx'  # ограничиваем длину
        except Exception as e:
            return f"Ошибка обработки DOCX {url}: {str(e)}", 'error'


class HTMLHandler(BaseHandler):
    async def can_handle(self, content_type: str, url: str) -> bool:
        return True  # will handle anything

    async def handle(self, content: bytes, url: str) -> tuple:
        try:
            # We have the content as bytes, we need to decode it for BeautifulSoup
            # We'll try to get the encoding from the response, or use chardet? 
            # For simplicity, we'll decode as utf-8 and ignore errors.
            html = content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            return text[:50000], 'web'  # ограничиваем длину
        except Exception as e:
            return f"Ошибка обработки HTML {url}: {str(e)}", 'error'


URL_PATTERN = re.compile(r'https?://\S+')


class AIAgent:
    def __init__(self, cohere_key: str = None, mistral_key: str = None):
        self.cohere_client = cohere.ClientV2(config.get_cohere_key(cohere_key))
        self.mistral_client = None
        mistral_api_key = config.get_mistral_key(mistral_key)
        if mistral_api_key:
            try:
                from mistralai import Mistral
                self.mistral_client = Mistral(api_key=mistral_api_key)
            except ImportError:
                pass
        # Initialize content handlers
        self.handlers = [
            PDFHandler(),
            DocxHandler(),
            HTMLHandler()
        ]
        # Initialize conversation history for chat mode
        self.conversation_history = []

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def extract_urls(self, text: str) -> list:
        return URL_PATTERN.findall(text)

    async def _fetch_url(self, url: str, session: aiohttp.ClientSession, retries: int = 3) -> tuple:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # YouTube special case (does not require downloading the video)
        if YouTubeTranscriptApi is not None and ('youtube.com' in url.lower() or 'youtu.be' in url.lower()):
            try:
                parsed = urllib.parse.urlparse(url)
                video_id = None
                if parsed.netloc in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
                    query = urllib.parse.parse_qs(parsed.query)
                    if 'v' in query:
                        video_id = query['v'][0]
                elif parsed.netloc == 'youtu.be':
                    video_id = parsed.path[1:]  # remove leading slash

                if video_id:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
                    text = ' '.join([item['text'] for item in transcript_list])
                    return text[:50000], 'youtube'  # ограничиваем длину
                else:
                    # If we couldn't extract video ID, fall through to downloading
                    pass
            except Exception as e:
                return f"Ошибка получения транскрипта YouTube {url}: {str(e)}", 'error'

        # For non-YouTube URLs, download the content with retry
        last_error = None
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=30, headers=headers) as response:
                    response.raise_for_status()
                    content = await response.read()
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Try to find a handler
                    for handler in self.handlers:
                        if await handler.can_handle(content_type, url):
                            result = await handler.handle(content, url)
                            return result, handler.__class__.__name__.replace('Handler', '').lower()
                    
                    # If no handler found, fallback to HTML
                    for handler in self.handlers:
                        if isinstance(handler, HTMLHandler):
                            result = await handler.handle(content, url)
                            return result, 'web'
                    
                    # If still not handled, return an error
                    return f"Не удалось обработать содержимое {url}: неизвестный тип контента", 'error'
            except Exception as e:
                last_error = e
                continue
        
        return f"Ошибка загрузки {url} после {retries} попыток: {str(last_error)}", 'error'

    async def fetch_urls_async(self, urls: list[str]) -> list[tuple]:
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_url(url, session) for url in urls]
            return await asyncio.gather(*tasks)

    def run(self, query: str) -> str:
        # 1. Извлекаем URL и загружаем контент
        urls = self.extract_urls(query)
        content_parts = []
        if urls:
            # Fetch all URLs in parallel
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self.fetch_urls_async(urls))
            loop.close()
            for url, (content, source_type) in zip(urls, results):
                content_parts.append(f"\n\n--- Содержание {url} (тип: {source_type}) ---\n{content}")
        else:
            contents = []

        # 2. Формируем полный запрос с контекстом
        if urls:
            full_query = (
                "Прочитай следующие сайты и ответь на вопрос:\n"
                + "\n".join(content_parts)
                + f"\n\nВопрос: {query}"
            )
        else:
            full_query = query

        # 3. Первый этап: Cohere – черновик ответа
        cohere_tokens = 0
        try:
            cohere_response = self.cohere_client.chat(
                model="command-a-03-2025",
                messages=[{"role": "user", "content": full_query}]
            )
            draft = cohere_response.message.content[0].text
            if hasattr(cohere_response, 'usage') and cohere_response.usage:
                tokens_obj = getattr(cohere_response.usage, 'tokens', None)
                if tokens_obj:
                    cohere_tokens = int(tokens_obj.input_tokens or 0) + int(tokens_obj.output_tokens or 0)
        except Exception as e:
            return f"Ошибка при вызове Cohere: {str(e)}", 0

        # Second stage: Mistral
        mistral_tokens = 0
        if self.mistral_client is not None:
            mistral_prompt = f"""
Ты — опытный ассистент, который улучшает, дополняет и исправляет ответы.

Вот исходный запрос пользователя (включая историю диалога и контент веб-страниц, если они были):
{full_query}

А это черновой ответ, сгенерированный другой моделью (Cohere):
{draft}

Пожалуйста, сделай следующее:
- Исправь любые фактические ошибки или неточности.
- Добавь важные детали, которых не хватает.
- Улучши стиль и читаемость, сохранив при этом доброжелательный и профессиональный тон.
- Если ответ уже хорош, просто верни его без изменений.

Итоговый улучшенный ответ:
"""
            try:
                mistral_response = self.mistral_client.chat(
                    model="mistral-large-latest",
                    messages=[{"role": "user", "content": mistral_prompt}]
                )
                mistral_tokens = mistral_response.usage.total_tokens if hasattr(mistral_response, 'usage') and mistral_response.usage else 0
                if hasattr(mistral_response, 'choices') and mistral_response.choices:
                    improved = mistral_response.choices[0].message.content
                elif hasattr(mistral_response, 'message'):
                    improved = mistral_response.message.content[0].text
                else:
                    improved = str(mistral_response)
                response = improved.strip()
            except Exception as e:
                response = f"{draft}\n\n[Примечание: не удалось улучшить ответ через Mistral: {e}]"

        else:
            response = draft

        # Add the agent's response to the conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        return response, cohere_tokens + mistral_tokens