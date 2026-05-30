import click
from max_ai.utils import HistoryManager

@click.command()
@click.option('--limit', default=10, help='Number of history entries to show')
def history(limit):
    """Show query history."""
    history_mgr = HistoryManager()
    entries = history_mgr.get(limit)
    if not entries:
        click.echo("История пуста")
        return
    for i, entry in enumerate(entries, 1):
        click.echo(f"\n{i}. [{entry['timestamp']}]")
        click.echo(f"   Запрос: {entry['query'][:50]}...")
        click.echo(f"   Ответ: {entry['response'][:100]}...")