from petrova.core.router import route_command
from petrova.ui.console import console


def start_shell():
    while True:
        command = console.input("\n[bold cyan]PETROVA ❯ [/bold cyan]").strip()

        if not command:
            continue

        handled = route_command(command)

        if handled:
            continue

        console.print()
        console.print("[bold red]PETROVA[/bold red]")
        console.print(f"Unknown command: [yellow]{command}[/yellow]")
        console.print("Type [cyan]help[/cyan] to view available commands.")