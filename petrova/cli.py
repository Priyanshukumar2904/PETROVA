"""
PETROVA CLI Application Entrypoint.
"""

from rich.panel import Panel

from petrova.config.settings import get_config
from petrova.config.wizard import run_onboarding_wizard
from petrova.core.server import is_server_running, start_server
from petrova.core.shell import start_shell
from petrova.memory.store import initialize as init_memory
from petrova.ui.banner import show_banner
from petrova.ui.console import console
from petrova.ui.greeting import get_greeting
from petrova.ui.status import get_status_table


def main():
    # 1. Initialize persistent memory database
    init_memory()

    # 2. Check if first-run onboarding is needed
    config = get_config()
    if not config.is_configured:
        show_banner()
        run_onboarding_wizard()
        # Reload config
        config = get_config()
    else:
        show_banner()

    console.print()

    # 3. Auto-start AI backend server if configured and offline
    if config.get("auto_start_server", True):
        host = config.get("server_host", "127.0.0.1")
        port = config.get("server_port", 8080)
        if not is_server_running(host, port):
            start_server()

    # 4. Personalized Greeting
    console.print(f"[bold cyan]{get_greeting()}[/bold cyan]")
    console.print()

    # 5. System Status Table
    console.print("[bold]System Status[/bold]")
    console.print(get_status_table())
    console.print()

    # 6. Ready Panel
    user_name = config.user_name
    console.print(
        Panel.fit(
            f"[bold green]PETROVA READY[/bold green]\n\n"
            f"[cyan]Awaiting Commands from {user_name}...[/cyan] [dim](Type [green]/help[/green] for commands)[/dim]",
            border_style="cyan",
        )
    )

    # 7. Start Interactive Shell
    start_shell()


if __name__ == "__main__":
    main()
