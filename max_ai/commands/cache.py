import click
from max_ai.core.config import config
from max_ai.utils import CacheManager
from max_ai.utils.cache import DEFAULT_CACHE_FILE

@click.command()
def cache_clear() -> None:
    """Clear the cache."""
    cache_mgr = CacheManager(config.cache_file or DEFAULT_CACHE_FILE)
    cache_mgr.clear()
    click.echo("Кеш очищен")
