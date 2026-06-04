import click
from rich.console import Console
from .commands import run, status, history, cache, interactive
from max_ai.core.config import config
from max_ai.core.rich_click import RichGroup

console = Console()

@click.group(cls=RichGroup, context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.option('--config', 'config_path', type=click.Path(exists=True, dir_okay=False), help='Path to YAML config file')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.version_option(version="0.1.0", prog_name="max-ai")
@click.pass_context
def cli(ctx, config_path, verbose):
    """MAX-AI: A console AI agent."""
    if config_path:
        config.set_config_file(config_path)
    config.verbose = verbose
    if verbose:
        console.log(f"[bright_green]Loaded configuration from:[/bright_green] {config_path or 'auto search locations'}")
        console.log(f"[bright_green]Cache file:[/bright_green] {config.cache_file}")
        console.log(f"[bright_green]History file:[/bright_green] {config.history_file}")
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))

cli.add_command(run.run)
cli.add_command(status.status)
cli.add_command(history.history)
cli.add_command(history.history_clear)
cli.add_command(cache.cache_clear)
cli.add_command(interactive.interactive)


def main():
    cli()


if __name__ == '__main__':
    main()
