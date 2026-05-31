import click
from .commands import run, status, history, cache
from max_ai.core import AIAgent

@click.group()
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