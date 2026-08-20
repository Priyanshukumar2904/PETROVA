"""
Server Management Commands (/server status, /server start, /server stop).
"""

from rich.panel import Panel
from petrova.ui.console import console
from petrova.core.server import start_server, stop_server, server_status


def server_command(args: list[str] = None):
    action = args[0].lower() if args else "status"

    if action == "start":
        console.print("[dim]Starting AI inference server...[/dim]")
        ok, msg = start_server()
        if ok:
            console.print(f"[bold green]✓ {msg}[/bold green]")
        else:
            console.print(f"[bold red]✗ {msg}[/bold red]")

    elif action == "stop":
        console.print("[dim]Stopping AI inference server...[/dim]")
        ok, msg = stop_server()
        if ok:
            console.print(f"[bold green]✓ {msg}[/bold green]")
        else:
            console.print(f"[bold yellow]{msg}[/bold yellow]")

    else:
        status_msg = server_status()
        console.print(Panel(status_msg, title="AI Server Status", border_style="cyan"))

    return True
