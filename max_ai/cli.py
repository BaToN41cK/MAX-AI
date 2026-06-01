import click
from rich.console import Console
from rich.panel import Panel
from .commands import run, status, history, cache
from max_ai.core import AIAgent

console = Console()

class RichCommand(click.Command):
    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        console.print(Panel(help_text, title=f"[bold blue]Help: {self.name}[/bold blue]", border_style="blue"))
        return ""

class RichGroup(click.Group):
    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        console.print(Panel(help_text, title="[bold blue]MAX-AI Help[/bold blue]", border_style="blue"))
        return ""

@click.group(cls=RichGroup, context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """MAX-AI: A console AI agent."""
    pass

cli.add_command(run.run)
cli.add_command(status.status)
cli.add_command(history.history)
cli.add_command(cache.cache_clear)

def main():
    cli()

if __name__ == '__main__':
    main()