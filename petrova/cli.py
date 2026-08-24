"""
PETROVA CLI Application Entrypoint.
Supports Interactive Terminal Shell and Desktop App GUI modes.
"""

import sys
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
from petrova.gui.desktop import ensure_desktop_entry


def main():
    # 1. Initialize persistent memory database & register desktop launcher
    init_memory()
    ensure_desktop_entry()

    # 2. Check if GUI mode was requested via command line flag
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--gui", "-g", "gui", "app"):
        from petrova.gui.app import launch_gui
        sys.exit(launch_gui())

    # 3. Check if first-run onboarding is needed
    config = get_config()
    if not config.is_configured:
        show_banner()
        run_onboarding_wizard()
        # Reload config
        config = get_config()
    else:
        show_banner()

    console.print()

    # 4. Auto-start AI backend server if configured and offline
    if config.get("auto_start_server", True):
        host = config.get("server_host", "127.0.0.1")
        port = config.get("server_port", 8080)
        if not is_server_running(host, port):
            start_server()

    # 5. Personalized Greeting
    console.print(f"[bold cyan]{get_greeting()}[/bold cyan]")
    console.print()

    # 6. System Status Table
    console.print("[bold]System Status[/bold]")
    console.print(get_status_table())
    console.print()

    # 7. Ready Panel with Instant GUI Trigger Prompt
    user_name = config.user_name
    console.print(
        Panel.fit(
            f"[bold green]PETROVA READY[/bold green]\n\n"
            f"[cyan]Awaiting Commands from {user_name}...[/cyan] [dim](Type [green]/help[/green] for commands)[/dim]\n"
            f"🚀 [bold cyan]Desktop App Interface:[/bold cyan] Type [bold green]/gui[/bold green] to initiate the full GUI & Neural Visualizer.",
            border_style="cyan",
        )
    )

    # 8. Start Interactive Shell
    start_shell()


if __name__ == "__main__":
    main()
