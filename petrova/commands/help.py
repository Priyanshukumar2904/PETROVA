from rich.panel import Panel

from petrova.ui.console import console


def help_command():
    console.print()

    console.print(
        Panel.fit(
            """[bold cyan]AVAILABLE COMMANDS[/bold cyan]

Use one of the following commands:

[green]help[/green]      Show available commands
[green]version[/green]   Display PETROVA version
[green]about[/green]     Learn about PETROVA
[green]clear[/green]     Clear the terminal screen
[green]exit[/green]      Exit PETROVA
""",
            title="PETROVA v0.1.0",
            border_style="cyan",
        )
    )

    return True