import click
from typing import Optional
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from max_ai.core.config import config
from max_ai.core.rich_click import RichCommand
from max_ai.utils import HistoryManager
from max_ai.utils.history import DEFAULT_HISTORY_FILE

console = Console()

@click.command(cls=RichCommand)
@click.option('--detail', type=int, help='Show full history entry by index (1 = latest)')
@click.option('--limit', default=10, type=int, help='Number of recent entries to show')
def history(detail: Optional[int], limit: int) -> None:
    """Show query history."""
    history_mgr = HistoryManager(config.history_file or DEFAULT_HISTORY_FILE)
    entries = history_mgr.get(limit)
    if not entries:
        console.print(Panel(Text("История пуста", style="bold yellow"), title="[bold yellow]History[/bold yellow]", border_style="yellow", box=box.ROUNDED))
        return

    if detail is not None:
        if detail < 1 or detail > len(entries):
            console.print(Panel(f"Неверный номер записи: {detail}", title="[bold red]Ошибка[/bold red]", border_style="red", box=box.ROUNDED))
            return
        entry = entries[detail - 1]
        source_text = "\n".join([f"{u} ({t})" for u, t in zip(entry.get('source_urls', []), entry.get('source_types', []))])
        console.print(Panel(
            f"[bold cyan]Запрос:[/bold cyan]\n{entry['query']}\n\n"
            f"[bold bright_green]Ответ:[/bold bright_green]\n{entry['response']}\n\n"
            f"[bold yellow]Модель:[/bold yellow] {entry.get('model_used', 'cohere')}\n"
            f"[bold yellow]Источники:[/bold yellow]\n{source_text if source_text else 'нет'}",
            title=f"[bold bright_green]История — запись {detail}[/bold bright_green]",
            border_style="bright_green",
            box=box.ROUNDED,
        ))
        return

    table = Table(title=f"История запросов (последние {len(entries)})", box=box.ROUNDED, border_style="bright_blue")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Время", style="magenta")
    table.add_column("Модель", style="bright_yellow")
    table.add_column("Запрос", style="bright_green")
    table.add_column("Ответ", style="white")

    for i, entry in enumerate(entries, 1):
        query_text = entry['query'][:50].replace("\n", " ")
        response_text = entry['response'][:100].replace("\n", " ")
        table.add_row(
            str(i),
            entry['timestamp'],
            entry.get('model_used', 'cohere'),
            query_text + ("..." if len(entry['query']) > 50 else ""),
            response_text + ("..." if len(entry['response']) > 100 else ""),
        )

    console.print(table)

@click.command(cls=RichCommand)
def history_clear() -> None:
    """Clear the saved history."""
    history_mgr = HistoryManager(config.history_file or DEFAULT_HISTORY_FILE)
    history_mgr.clear()
    console.print(Panel("История успешно очищена", title="[bold bright_green]History Clear[/bold bright_green]", border_style="bright_green", box=box.ROUNDED))
