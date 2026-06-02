import time
import click
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from max_ai.core import AIAgent
from max_ai.core.config import config
from max_ai.core.rich_click import RichCommand
from max_ai.constants import URL_VALIDATION_PATTERN
from max_ai.utils import CacheManager, HistoryManager
from max_ai.utils.cache import DEFAULT_CACHE_FILE
from max_ai.utils.history import DEFAULT_HISTORY_FILE

console = Console()


def classify_source(url: str) -> tuple[str, str]:
    lower = url.lower()
    if lower.endswith('.pdf'):
        return 'PDF', 'blue'
    if lower.endswith('.docx') or lower.endswith('.doc'):
        return 'DOCX', 'blue'
    if lower.endswith('.pptx'):
        return 'PPTX', 'blue'
    if lower.endswith('.xlsx') or lower.endswith('.xls'):
        return 'XLSX', 'blue'
    if 'youtube.com' in lower or 'youtu.be' in lower:
        return 'YOUTUBE', 'red'
    if lower.endswith('.txt') or lower.endswith('.md'):
        return 'TEXT', 'blue'
    return 'WEB', 'cyan'


def fast_typewriter(text: str, delay: float = 0.02, chunk_size: int = 16, style: str = "bright_green") -> None:
    if not text:
        return
    normalized = text.replace('\r\n', '\n')
    for i in range(0, len(normalized), chunk_size):
        chunk = normalized[i:i + chunk_size]
        console.print(chunk, style=style, end="", markup=False)
        console.file.flush()
        time.sleep(delay)
    console.print("")


def render_response(text: str, error: bool = False) -> None:
    if error:
        console.print(Panel(Text(text, style="bold red"), title="Ошибка", border_style="red"))
        return
    if '\n' in text or len(text) > 200 or '```' in text:
        console.print(Panel(Text(text, style="bright_green"), title="Ответ", border_style="bright_green"))
    else:
        fast_typewriter(text, style="bright_green")


@click.command(cls=RichCommand)
@click.argument('query', nargs=-1)
@click.option('--no-cache', is_flag=True, help='Do not use cache')
@click.option('--cohere-key', help='Specify which Cohere API key to use')
@click.option('--ttl', default=3600, help='Cache TTL in seconds')
@click.option('--model', help='Cohere model to use (default: command-a-03-2025)')
@click.option('--no-mistral', is_flag=True, help='Do not use Mistral for answer refinement')
@click.option('--source', multiple=True, help='Additional source URLs to include')
def run(query, no_cache, cohere_key, ttl, model, no_mistral, source):
    query = " ".join(query).strip()
    extra_urls = [url.strip() for url in source if url.strip()]

    if not query and not extra_urls:
        click.echo("Пожалуйста, укажите запрос или источник.")
        return

    agent = AIAgent(cohere_key=cohere_key, model=model, use_mistral=not no_mistral)
    cache_mgr = CacheManager(config.cache_file or DEFAULT_CACHE_FILE)
    history_mgr = HistoryManager(config.history_file or DEFAULT_HISTORY_FILE)

    query_urls = agent.extract_urls(query)
    explicit_urls = [url for url in extra_urls if URL_VALIDATION_PATTERN.match(url)]
    urls = list(dict.fromkeys(query_urls + explicit_urls))
    cache_key = query
    if urls:
        cache_key = query + ' ' + ' '.join(urls)

    if not no_cache:
        cached = cache_mgr.get(cache_key)
        if cached:
            render_response(cached.response)
            return

    if urls:
        console.print(f"Найдено URL: {len(urls)}", style="bold bright_green")
        for i, url in enumerate(urls, 1):
            tag, color = classify_source(url)
            console.print(f"[bright_green]{i}.[/bright_green] [{color}]{tag}[/] {url}")
        with console.status("[bright_green]Получение ответа от AI...[/bright_green]", spinner="dots"):
            response, tokens = agent.run(query, sources=urls)
    else:
        with console.status("[bright_green]Получение ответа от AI...[/bright_green]", spinner="dots"):
            response, tokens = agent.run(query, sources=[])

    if not no_cache:
        cache_mgr.set(cache_key, response, ttl)

    model_used = "cohere"
    if agent.use_mistral and agent.mistral_client:
        model_used = "mistral-enhanced"

    history_mgr.add(
        query,
        response,
        model_used=model_used,
        tokens=tokens,
        source_urls=urls,
        source_types=[classify_source(url)[0] for url in urls],
    )

    if response is not None and response.startswith("Ошибка"):
        render_response(response, error=True)
    else:
        render_response(response)
