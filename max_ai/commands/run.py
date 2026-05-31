import time
import click
import shutil
import textwrap
from typing import Optional
from colorama import Fore, Style, init
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from max_ai.core import AIAgent
from max_ai.core.config import config
from max_ai.utils import CacheManager, HistoryManager
from max_ai.utils.cache import DEFAULT_CACHE_FILE
from max_ai.utils.history import DEFAULT_HISTORY_FILE

init()
console = Console()

def wrapped_print(text: Optional[str], width: Optional[int] = None, color: Optional[str] = None, source_type: Optional[str] = None) -> None:
    if text is None:
        text = ''
    if width is None:
        width = shutil.get_terminal_size().columns
    
    if source_type:
        colors = {
            'web': Fore.BLUE,
            'pdf': Fore.RED,
            'docx': Fore.GREEN,
            'youtube': Fore.YELLOW,
            'text': Fore.WHITE
        }
        click.echo(colors.get(source_type, Fore.WHITE) + f"[{source_type.upper()}] " + Style.RESET_ALL, end='')
    
    paragraphs = text.split('\n')
    for para in paragraphs:
        if para.strip() == '':
            click.echo('')
            continue
        wrapped = textwrap.fill(para, width=width, replace_whitespace=False)
        if color:
            click.echo(color + wrapped + Style.RESET_ALL)
        else:
            click.echo(wrapped)

@click.command()
@click.argument('query')
@click.option('--no-cache', is_flag=True, help='Do not use cache')
@click.option('--cohere-key', help='Specify which Cohere API key to use')
@click.option('--ttl', default=3600, help='Cache TTL in seconds')
@click.option('--model', help='Cohere model to use (default: command-a-03-2025)')
def run(query, no_cache, cohere_key, ttl, model):
    """Run a query against the AI agent."""
    agent = AIAgent(cohere_key=cohere_key, model=model)
    cache_mgr = CacheManager(config.cache_file or DEFAULT_CACHE_FILE)
    history_mgr = HistoryManager(config.history_file or DEFAULT_HISTORY_FILE)

    if not no_cache:
        cached = cache_mgr.get(query)
        if cached:
            wrapped_print(cached.response)
            return

    start_time = time.time()
    
    with console.status("[bold blue]Анализ запроса...[/bold blue]", spinner="dots"):
        urls = agent.extract_urls(query)
    
    if urls:
        with Progress(
            TextColumn("[bold yellow]Загрузка URL:"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("", total=len(urls))
            for url in urls:
                progress.advance(task)
            response, tokens = agent.run(query)
    else:
        with console.status("[bold green]Получение ответа от AI...[/bold green]", spinner="dots"):
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
        wrapped_print(response, color=Fore.RED)
        click.echo(f"\nExecution time: {elapsed:.2f}s")
    else:
        wrapped_print(response, color=Fore.GREEN)
        click.echo(f"\nExecution time: {elapsed:.2f}s, Tokens: {tokens}")
