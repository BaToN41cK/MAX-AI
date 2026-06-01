import time
import click
from typing import Optional
from colorama import init, Fore, Style
import sys
from rich.console import Console
from max_ai.core import AIAgent
from max_ai.core.config import config
from max_ai.utils import CacheManager, HistoryManager
from max_ai.utils.cache import DEFAULT_CACHE_FILE
from max_ai.utils.history import DEFAULT_HISTORY_FILE

init()
console = Console()


def classify_source(url: str) -> tuple[str, str]:
    """Return a short tag and preferred color for a given URL."""
    lower = url.lower()
    if lower.endswith('.pdf'):
        return 'PDF', 'red'
    if lower.endswith('.docx') or lower.endswith('.doc'):
        return 'DOCX', 'magenta'
    if lower.endswith('.pptx'):
        return 'PPTX', 'yellow'
    if lower.endswith('.xlsx') or lower.endswith('.xls'):
        return 'XLSX', 'green'
    if 'youtube.com' in lower or 'youtu.be' in lower:
        return 'YOUTUBE', 'cyan'
    if lower.endswith('.txt') or lower.endswith('.md'):
        return 'TEXT', 'white'
    return 'WEB', 'cyan'


def fast_typewriter(text: str, delay: float = 0.02, chunk_size: int = 16, style: str = "green") -> None:
    """Write `text` to stdout in fast chunks to simulate a typewriter.

    Defaults are tuned for a very fast effect that's still perceptible.
    """
    if not text:
        return
    start = Fore.GREEN if style == "green" else ""
    end = Style.RESET_ALL
    normalized = text.replace('\r\n', '\n')
    sys.stdout.write(start)
    sys.stdout.flush()
    for i in range(0, len(normalized), chunk_size):
        chunk = normalized[i:i + chunk_size]
        sys.stdout.write(chunk)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end + "\n")
    sys.stdout.flush()


@click.command()
@click.argument('query', nargs=-1)
@click.option('--no-cache', is_flag=True, help='Do not use cache')
@click.option('--cohere-key', help='Specify which Cohere API key to use')
@click.option('--ttl', default=3600, help='Cache TTL in seconds')
@click.option('--model', help='Cohere model to use (default: command-a-03-2025)')
def run(query, no_cache, cohere_key, ttl, model):
    """Run a query against the AI agent."""
    query = " ".join(query).strip()
    if not query:
        click.echo("Пожалуйста, укажите запрос.")
        return
    agent = AIAgent(cohere_key=cohere_key, model=model)
    cache_mgr = CacheManager(config.cache_file or DEFAULT_CACHE_FILE)
    history_mgr = HistoryManager(config.history_file or DEFAULT_HISTORY_FILE)

    if not no_cache:
        cached = cache_mgr.get(query)
        if cached:
            fast_typewriter(cached.response)
            return

    urls = agent.extract_urls(query)

    start_time = time.time()
    if urls:
        console.print(f"Найдено URL: {len(urls)}", style="bold green")
        for i, url in enumerate(urls, 1):
            tag, color = classify_source(url)
            console.print(f"{i}. [{color}]{tag}[/] {url}")
        with console.status("[green]Получение ответа от AI...[/green]", spinner="dots"):
            response, tokens = agent.run(query)
    else:
        with console.status("[green]Получение ответа от AI...[/green]", spinner="dots"):
            response, tokens = agent.run(query)

    elapsed = time.time() - start_time

    if not no_cache:
        cache_mgr.set(query, response, ttl)

    model_used = "cohere"
    is_mistral_enhanced = (
        "[Примечание: не удалось улучшить ответ через Mistral" not in str(response)
        and "Mistral" in str(response)
    )
    if agent.mistral_client and is_mistral_enhanced:
        model_used = "mistral-enhanced"

    history_mgr.add(query, response, model_used=model_used, tokens=tokens)

    if response is not None and response.startswith("Ошибка"):
        console.print("Ошибка при получении ответа", style="bold red")
        fast_typewriter(response, style="red")
    else:
        # Если в ответе есть фраза, с которой пользователь хочет начать печать,
        # начинаем машинописный вывод с этой фразы, а предшествующий текст выводим обычным текстом.
        marker = "Создание нового кода"
        try:
            idx = response.find(marker)
        except Exception:
            idx = -1

        if idx is not None and idx >= 0:
            pre = response[:idx].strip()
            post = response[idx:]
            if pre:
                # Показываем краткий префейс в обычном цвете
                console.print(pre)
            fast_typewriter(post, style="green")
        else:
            fast_typewriter(response, style="green")
