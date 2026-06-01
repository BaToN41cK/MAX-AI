import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from max_ai.core.config import config
from max_ai.utils import HistoryManager
from max_ai.utils.history import DEFAULT_HISTORY_FILE

console = Console()

@click.command()
@click.option('--days', default=7, help='Number of days to analyze (default: 7)')
def status(days: int) -> None:
    """Check status and show usage statistics."""
    console.print(Panel.fit(
        "[bold blue]MAX-AI Status[/bold blue]",
        border_style="blue"
    ))
    
    cohere_status = Text("configured", style="bold green") if config.cohere_api_key else Text("missing", style="bold red")
    mistral_status = Text("configured", style="bold green") if config.mistral_api_key else Text("not set", style="bold yellow")
    click.echo(f"API: Cohere={cohere_status}, Mistral={mistral_status}")
    
    history_file = config.history_file or DEFAULT_HISTORY_FILE
    history_mgr = HistoryManager(history_file=history_file)
    stats_data = history_mgr.get_stats(days=days)
    
    table = Table(title=f"Usage Statistics (last {days} days)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total Requests", str(stats_data['total_requests']))
    table.add_row("Total Tokens", f"{stats_data['total_tokens']:,}")
    table.add_row("Estimated Cost (USD)", f"${stats_data['cost_estimate_usd']:.4f}")
    console.print(table)
    
    if stats_data['daily_breakdown']:
        click.echo("\n[bold]Requests by day:[/bold]")
        with Progress(BarColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            for day, count in list(stats_data['daily_breakdown'].items())[-7:]:
                bar = progress.add_task(day, total=max(stats_data['daily_breakdown'].values(), default=1))
                progress.update(bar, completed=count)
