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

@click.command()
def chat():
    """Start an interactive chat session."""
    agent = AIAgent()
    click.echo("Начало чата. Введите 'exit' или 'quit' для завершения, 'clear' для очистки истории.")
    while True:
        user_input = click.prompt('\nВы', type=str, prompt_suffix=': ')
        if user_input.lower() in ['exit', 'quit']:
            break
        if user_input.lower() == 'clear':
            agent.clear_history()
            click.echo("История очищена")
            continue
        response = agent.chat(user_input)
        click.echo(f"\nАгент: {response}")

cli.add_command(chat)

def main():
    cli()

if __name__ == '__main__':
    main()