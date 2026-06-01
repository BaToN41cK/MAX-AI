import click
from rich.console import Console
from rich.panel import Panel
from max_ai.core.config import config
from max_ai.utils import CacheManager
from max_ai.utils.cache import DEFAULT_CACHE_FILE

console = Console()

@click.command()
def cache_clear() -> None:
    """Clear the cache."""
    cache_mgr = CacheManager(config.cache_file or DEFAULT_CACHE_FILE)
    cache_mgr.clear()
    console.print(Panel("Кеш успешно очищен", title="[bold green]Cache Clear[/bold green]", border_style="green"))
