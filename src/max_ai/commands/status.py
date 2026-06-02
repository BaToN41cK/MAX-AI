import click
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from max_ai.core.config import config
from max_ai.core.rich_click import RichCommand
from max_ai.utils import HistoryManager
from max_ai.utils.history import DEFAULT_HISTORY_FILE

console = Console()

@click.command(cls=RichCommand)
@click.option('--days', default=7, help='Number of days to analyze (default: 7)')
def status(days: int) -> None:
    """Check status and show usage statistics."""
    console.print(Panel.fit(
        "[bold blue]MAX-AI Status[/bold blue]",
        border_style="blue",
        box=box.ROUNDED,
    ))
    
    cohere_status = Text("configured", style="bold bright_green") if config.cohere_api_key else Text("missing", style="bold red")
    mistral_status = Text("configured", style="bold bright_green") if config.mistral_api_key else Text("not set", style="bold yellow")
    console.print(Panel(
        f"[bold]Cohere API:[/bold] {cohere_status}\n[bold]Mistral API:[/bold] {mistral_status}",
        title="[bold]API Configuration[/bold]",
        border_style="cyan",
        box=box.ROUNDED,
    ))
    
    history_file = config.history_file or DEFAULT_HISTORY_FILE
    history_mgr = HistoryManager(history_file=history_file)
    stats_data = history_mgr.get_stats(days=days)
    
    summary = Text()
    summary.append(f"Total Requests: ", style="cyan")
    summary.append(f"{stats_data['total_requests']}\n", style="bold bright_green")
    summary.append(f"Total Tokens: ", style="cyan")
    summary.append(f"{stats_data['total_tokens']:,}\n", style="bright_green")
    summary.append(f"Average Tokens: ", style="cyan")
    summary.append(f"{stats_data['average_tokens']:.1f}\n", style="bright_green")
    summary.append(f"Unique Domains: ", style="cyan")
    summary.append(f"{stats_data['unique_domains']}\n", style="bright_green")
    summary.append(f"Estimated Cost: ", style="cyan")
    summary.append(f"${stats_data['cost_estimate_usd']:.4f}\n", style="bright_green")

    if stats_data['model_usage']:
        models = ", ".join([f"{m} ({c})" for m, c in stats_data['model_usage'].items()])
        summary.append("\nModel usage: ", style="magenta")
        summary.append(models, style="magenta")

    console.print(Panel(summary, title=f"Usage Summary ({days} days)", border_style="bright_blue", box=box.SQUARE))

    if stats_data['top_domains']:
        dom_text = Text()
        for domain, count in stats_data['top_domains']:
            dom_text.append(f"{domain}: ", style="cyan")
            dom_text.append(f"{count}\n", style="bright_green")
        console.print(Panel(dom_text, title="Top Domains", border_style="magenta", box=box.SQUARE))

    if stats_data['daily_breakdown']:
        console.rule("[bold yellow]Requests by day (recent)[/bold yellow]")
        with Progress(BarColumn(bar_width=40), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            max_value = max(stats_data['daily_breakdown'].values(), default=1)
            for day, count in list(stats_data['daily_breakdown'].items())[-7:]:
                bar = progress.add_task(day, total=max_value)
                progress.update(bar, completed=count)
