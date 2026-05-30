import click
import os
import sys
sys_path_addition = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path_addition not in sys.path:
    sys.path.insert(0, sys_path_addition)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from max_ai.utils import HistoryManager

console = Console()

@click.command()
@click.option('--days', default=7, help='Number of days to analyze (default: 7)')
def status(days):
    """Check status and show usage statistics."""
    from max_ai.core.config import config
    
    console.print(Panel.fit(
        "[bold blue]MAX-AI Status[/bold blue]",
        border_style="blue"
    ))
    
    # API status
    click.echo("Status: OK")
    click.echo(f"API keys: Cohere={'configured' if config.cohere_api_key else 'missing'}, Mistral={'configured' if config.mistral_api_key else 'missing'}")
    
    # Statistics
    history_mgr = HistoryManager()
    stats_data = history_mgr.get_stats(days=days)
    
    table = Table(title="Usage Statistics (last {} days)".format(days))
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total Requests", str(stats_data['total_requests']))
    table.add_row("Total Tokens", f"{stats_data['total_tokens']:,}")
    table.add_row("Estimated Cost (USD)", f"${stats_data['cost_estimate_usd']:.4f}")
    console.print(table)