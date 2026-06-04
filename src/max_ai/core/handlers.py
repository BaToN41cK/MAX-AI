import io
import json
import zipfile
import csv
from typing import Optional
from bs4 import BeautifulSoup
from .config import config
import logging

logger = logging.getLogger(__name__)


class EPubHandler:
    async def can_handle(self, content_type: str, url: str) -> bool:
        return 'application/epub+zip' in content_type or url.lower().endswith('.epub')

    async def handle(self, content: bytes, url: str) -> tuple[str, str]:
        try:
            epub_file = io.BytesIO(content)
            with zipfile.ZipFile(epub_file) as z:
                text = ""
                for file in z.namelist():
                    if file.endswith('.xhtml') or file.endswith('.html'):
                        with z.open(file) as f:
                            html_content = f.read().decode('utf-8', errors='ignore')
                            soup = BeautifulSoup(html_content, 'html.parser')
                            text += soup.get_text(separator='\n', strip=True) + "\n"
                return text[:config.get("max_content_length", 50000)], 'epub'
        except Exception as e:
            logger.error(f"Ошибка обработки EPUB {url}: {str(e)}")
            return f"Ошибка обработки EPUB {url}: {str(e)}", 'error'


class CSVHandler:
    async def can_handle(self, content_type: str, url: str) -> bool:
        return 'text/csv' in content_type or url.lower().endswith('.csv')

    async def handle(self, content: bytes, url: str) -> tuple[str, str]:
        try:
            csv_content = content.decode('utf-8', errors='ignore')
            csv_reader = csv.reader(io.StringIO(csv_content))
            text = ""
            for row in csv_reader:
                text += ", ".join(row) + "\n"
            return text[:config.get("max_content_length", 50000)], 'csv'
        except Exception as e:
            logger.error(f"Ошибка обработки CSV {url}: {str(e)}")
            return f"Ошибка обработки CSV {url}: {str(e)}", 'error'


class JSONHandler:
    async def can_handle(self, content_type: str, url: str) -> bool:
        return 'application/json' in content_type or url.lower().endswith('.json')

    async def handle(self, content: bytes, url: str) -> tuple[str, str]:
        try:
            json_content = content.decode('utf-8', errors='ignore')
            data = json.loads(json_content)
            text = json.dumps(data, indent=2, ensure_ascii=False)
            return text[:config.get("max_content_length", 50000)], 'json'
        except Exception as e:
            logger.error(f"Ошибка обработки JSON {url}: {str(e)}")
            return f"Ошибка обработки JSON {url}: {str(e)}", 'error'