"""
Configuration Management & Quick Settings Commands for PETROVA.
Supports full wizard re-run (/setup or /config) or targeted changes (/config name, /config model, etc.)
"""

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from petrova.ui.console import console
from petrova.config.settings import get_config
from petrova.config.wizard import run_onboarding_wizard
from petrova.memory.store import get_db_size_mb, get_memory_count


def show_config_panel():
    """Display current active configuration settings."""
    config = get_config()
    perm_mode = config.get("permission_mode", "confirm").upper()
    quota = config.get("memory_storage_mb", 500)
    quota_str = f"{quota} MB" if quota > 0 else "Unlimited"

    table = Table(show_header=False, box=None, expand=False)
    table.add_column("Setting", style="bold cyan", width=20)
    table.add_column("Value")

    table.add_row("User Name", f"[bold green]{config.user_name}[/bold green]")
    table.add_row("Model Name", f"[bold]{config.model_name}[/bold]")
    table.add_row("Inference Backend", f"{config.backend} (Port {config.get('server_port', 8080)})")
    table.add_row("Permissions", f"[bold yellow]{perm_mode}[/bold yellow]")
    table.add_row("Memory Quota", f"{quota_str} [dim]({get_memory_count()} items, {get_db_size_mb()} MB)[/dim]")
    table.add_row("Streaming Output", "Enabled" if config.get("stream_output", True) else "Disabled")
    table.add_row("Auto-Start Server", "Enabled" if config.get("auto_start_server", True) else "Disabled")

    console.print()
    console.print(Panel(table, title="⚙️ PETROVA Active Configuration", border_style="cyan"))
    console.print("[dim]Use [green]/config <setting>[/green] or [green]/setup[/green] to modify.[/dim]\n")


def config_command(args: list[str] = None):
    """Handle /config and /setup commands."""
    config = get_config()

    if not args:
        # If bare /config or /setup without subcommands, run full wizard
        return run_onboarding_wizard(force=True)

    action = args[0].lower()

    if action in ("view", "show", "info", "status"):
        show_config_panel()
        return True

    elif action in ("name", "user"):
        if len(args) > 1:
            new_name = " ".join(args[1:]).strip()
        else:
            new_name = Prompt.ask("[green]Enter your preferred name[/green]", default=config.user_name).strip()
        if new_name:
            config.set("user_name", new_name)
            console.print(f"[bold green]✓ User name updated to:[/bold green] {new_name}")

    elif action in ("model", "backend"):
        console.print("[dim]Launching model selection wizard...[/dim]")
        return run_onboarding_wizard(force=True)

    elif action in ("permissions", "perm"):
        if len(args) > 1 and args[1].lower() in ("confirm", "autonomous", "read_only"):
            mode = args[1].lower()
        else:
            console.print("\n[bold]Select Permission Mode:[/bold]")
            console.print("1. [bold green]confirm[/bold green] — Ask [y/N] before running any command (Recommended)")
            console.print("2. [bold yellow]autonomous[/bold yellow] — Auto-run safe checks; confirm destructive commands")
            console.print("3. [bold red]read_only[/bold red] — Suggestions only (never execute)")
            choice = Prompt.ask("[green]Choose mode[/green]", choices=["1", "2", "3"], default="1")
            mode_map = {"1": "confirm", "2": "autonomous", "3": "read_only"}
            mode = mode_map[choice]

        config.set("permission_mode", mode)
        console.print(f"[bold green]✓ Permission mode set to:[/bold green] {mode.upper()}")

    elif action in ("memory", "quota", "storage"):
        if len(args) > 1 and args[1].isdigit():
            mb = int(args[1])
        else:
            console.print("\n[bold]Select Memory Storage Quota:[/bold]")
            console.print("1. 100 MB (~50,000 memories)")
            console.print("2. 500 MB (~250,000 memories) — Recommended")
            console.print("3. 2000 MB (2 GB heavy persistent store)")
            console.print("4. Unlimited")
            choice = Prompt.ask("[green]Choose quota[/green]", choices=["1", "2", "3", "4"], default="2")
            q_map = {"1": 100, "2": 500, "3": 2000, "4": 0}
            mb = q_map[choice]

        config.set("memory_storage_mb", mb)
        console.print(f"[bold green]✓ Memory quota set to:[/bold green] {mb if mb > 0 else 'Unlimited'} MB")

    elif action in ("reset", "wizard", "all"):
        return run_onboarding_wizard(force=True)

    else:
        console.print(f"[yellow]Unknown config option '{action}'.[/yellow]")
        console.print("[dim]Options: /config view, /config name, /config model, /config permissions, /config memory, /setup[/dim]")

    return True
