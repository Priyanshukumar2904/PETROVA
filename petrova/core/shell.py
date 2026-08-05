from petrova.brain.brain import ask
from petrova.core.router import route_command
from petrova.ui.console import console


def start_shell():
    while True:
        command = console.input(
            "\n[bold cyan]PETROVA ❯ [/bold cyan]"
        ).strip()

        if not command:
            continue

        if route_command(command):
            continue

        console.print()
        console.print("[bold green]PETROVA[/bold green]")

        try:
            response = ask(command)
            console.print(response)
        except Exception as error:
            console.print(f"[bold red]Error:[/bold red] {error}")