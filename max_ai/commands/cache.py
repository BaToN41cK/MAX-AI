import click
from max_ai.utils import CacheManager

@click.command()
def cache_clear():
    """Clear the cache."""
    cache_mgr = CacheManager()
    cache_mgr.clear()
    click.echo("Кеш очищен")