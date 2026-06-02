import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def format_help_text(help_text: str) -> Text:
    text = Text()
    for line in help_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Usage:"):
            text.append(line + "\n", style="bold bright_cyan")
        elif stripped in ("Options:", "Commands:"):
            text.append(line + "\n", style="bold bright_yellow")
        elif stripped.startswith("-h,") or stripped.startswith("--help") or stripped.startswith("--version"):
            text.append(line + "\n", style="bright_white")
        elif stripped.startswith("run") or stripped.startswith("status") or stripped.startswith("history") or stripped.startswith("cache-clear") or stripped.startswith("history-clear"):
            text.append(line + "\n", style="bright_cyan")
        else:
            text.append(line + "\n")
    return text


class RichCommand(click.Command):
    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        console.print(
            Panel(format_help_text(help_text), title=f"[bold bright_blue]Help: {self.name}[/bold bright_blue]", border_style="bright_blue")
        )
        return ""


class RichGroup(click.Group):
    command_class = RichCommand

    def get_help(self, ctx):
        help_text = super().get_help(ctx)
        console.print(
            Panel(format_help_text(help_text), title="[bold bright_blue]MAX-AI Help[/bold bright_blue]", border_style="bright_blue")
        )
        return ""
