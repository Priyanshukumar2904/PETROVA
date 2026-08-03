from rich.panel import Panel

from petrova.core.shell import start_shell
from petrova.ui.banner import show_banner
from petrova.ui.console import console
from petrova.ui.greeting import get_greeting
from petrova.ui.status import get_status_table


def main():
    # ==========================================================
    # PETROVA Banner
    # ==========================================================
    show_banner()

    console.print()

    # ==========================================================
    # Greeting
    # ==========================================================
    console.print(f"[bold cyan]{get_greeting()}[/bold cyan]")

    console.print()

    # ==========================================================
    # System Status
    # ==========================================================
    console.print("[bold]System Status[/bold]")
    console.print(get_status_table())

    console.print()

    # ==========================================================
    # Ready Panel
    # ==========================================================
    console.print(
        Panel.fit(
            "[bold green]PETROVA READY[/bold green]\n\n"
            "[cyan]Awaiting Commands...[/cyan]",
            border_style="cyan",
        )
    )

    # ==========================================================
    # Start Interactive Shell
    # ==========================================================
    start_shell()