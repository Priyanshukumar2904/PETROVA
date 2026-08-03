from petrova.ui.console import console


def start_shell():
    while True:
        command = console.input("\n[bold cyan]PETROVA ❯ [/bold cyan]").strip()

        if not command:
            continue

        if command.lower() == "exit":
            console.print("\n[bold green]PETROVA[/bold green]")
            console.print("Session terminated.")
            break

        console.print(f"\n[bold green]PETROVA[/bold green]")
        console.print(f"You entered: [cyan]{command}[/cyan]")