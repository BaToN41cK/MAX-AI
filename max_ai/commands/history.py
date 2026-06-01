import click
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from max_ai.core.config import config
from max_ai.utils import HistoryManager
from max_ai.utils.history import DEFAULT_HISTORY_FILE

console = Console()

@click.command()
@click.argument('limit', required=False, default=10, type=int)
def history(limit: int) -> None:
    """Show query history."""
    history_mgr = HistoryManager(config.history_file or DEFAULT_HISTORY_FILE)
    entries = history_mgr.get(limit)
    if not entries:
        console.print(Panel("История пуста", title="[bold yellow]History[/bold yellow]", border_style="yellow", box=box.ROUNDED))
        return

    if len(entries) == 1:
        entry = entries[0]
        console.print(Panel(
            f"[bold cyan]Запрос:[/bold cyan]\n{entry['query']}\n\n[bold green]Ответ:[/bold green]\n{entry['response']}",
            title="[bold green]История — последняя запись[/bold green]",
            border_style="green",
            box=box.ROUNDED,
        ))
        return

    table = Table(title=f"История запросов (последние {len(entries)})", box=box.ROUNDED, border_style="bright_blue")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Время", style="magenta")
    table.add_column("Запрос", style="green")
    table.add_column("Ответ", style="white")

    for i, entry in enumerate(entries, 1):
        query_text = entry['query'][:50].replace("\n", " ")
        response_text = entry['response'][:100].replace("\n", " ")
        table.add_row(
            str(i),
            entry['timestamp'],
            query_text + ("..." if len(entry['query']) > 50 else ""),
            response_text + ("..." if len(entry['response']) > 100 else "")
        )

    console.print(table)
