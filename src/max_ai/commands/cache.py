import click
from rich.console import Console
from rich.panel import Panel
from max_ai.core.config import config
from max_ai.core.rich_click import RichCommand
from max_ai.utils import CacheManager
from max_ai.utils.cache import DEFAULT_CACHE_FILE

console = Console()

@click.command(cls=RichCommand)
def cache_clear() -> None:
    """Clear the cache."""
    cache_mgr = CacheManager(config.cache_file or DEFAULT_CACHE_FILE)
    cache_mgr.clear()
    console.print(Panel(Text("Кеш успешно очищен", style="bright_green"), title="[bold bright_green]Cache Clear[/bold bright_green]", border_style="bright_green"))
