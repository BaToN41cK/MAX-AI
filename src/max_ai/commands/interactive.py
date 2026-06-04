import click
from rich.console import Console
from rich.prompt import Prompt
from max_ai.core.agent import AIAgent
from max_ai.core.config import config

console = Console()


@click.command()
@click.option('--cohere-key', help='Cohere API key')
@click.option('--mistral-key', help='Mistral API key')
@click.option('--model', help='Model name')
@click.option('--use-mistral/--no-use-mistral', default=True, help='Use Mistral API')
def interactive(cohere_key, mistral_key, model, use_mistral):
    """
    Запускает интерактивный режим для диалога с AI.
    """
    try:
        agent = AIAgent(
            cohere_key=cohere_key,
            mistral_key=mistral_key,
            model=model,
            use_mistral=use_mistral
        )
        console.print("[bold bright_green]Интерактивный режим запущен. Введите 'exit' для выхода.[/bold bright_green]")
        
        while True:
            try:
                query = Prompt.ask("[bold bright_cyan]Вы[/bold bright_cyan]")
                if query.lower() == 'exit':
                    break
                
                with console.status("[bold bright_green]Обработка запроса...[/bold bright_green]", spinner="dots"):
                    response, tokens = agent.run(query)
                
                console.print("[bold bright_yellow]AI[/bold bright_yellow]: ", end="")
                console.print(response)
                console.print(f"[bright_black]Использовано токенов: {tokens}[/bright_black]")
            except Exception as e:
                console.print(f"[bold bright_red]Ошибка: {str(e)}[/bold bright_red]")
        
        console.print("[bold bright_green]Интерактивный режим завершен.[/bold bright_green]")
    except Exception as e:
        console.print(f"[bold bright_red]Ошибка при инициализации агента: {str(e)}[/bold bright_red]")