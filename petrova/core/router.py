"""
Slash Command Router for PETROVA.
Dispatches commands to corresponding handlers or returns False for AI processing.
"""

from petrova.commands.help import help_command
from petrova.commands.version import version_command
from petrova.commands.about import about_command
from petrova.commands.clear import clear_command
from petrova.commands.exit import exit_command
from petrova.commands.server import server_command
from petrova.commands.memory import memory_command
from petrova.commands.config import config_command
from petrova.tools.executor import execute_command
from petrova.ui.status import get_status_table
from petrova.ui.console import console


def route_command(user_input: str) -> bool:
    """Check if input is a built-in slash command or shell escape and execute it."""
    trimmed = user_input.strip()
    if not trimmed:
        return False

    # Quick shell escape: "!ls -la" or "!df -h"
    if trimmed.startswith("!"):
        cmd = trimmed[1:].strip()
        if cmd:
            execute_command(cmd)
            return True

    # Normalize leading slash: "/help" -> "help"
    cmd_line = trimmed[1:] if trimmed.startswith("/") else trimmed
    parts = cmd_line.split()
    primary = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    # Map commands
    if primary in ("help", "?"):
        return help_command()

    elif primary in ("goal", "plan", "task"):
        if not args:
            console.print("[yellow]Usage:[/yellow] [green]/goal <multi-step objective>[/green]")
            return True
        from petrova.brain.planner import execute_goal
        execute_goal(" ".join(args))
        return True

    elif primary in ("run", "exec", "sh", "bash"):

        if not args:
            console.print("[yellow]Usage: /run <command>[/yellow] (e.g. [green]/run df -h[/green])")
            return True
        execute_command(" ".join(args))
        return True

    elif primary in ("voice", "speak", "talk"):
        from petrova.commands.voice import voice_command
        return voice_command(args)

    elif primary in ("listen", "mic", "hear"):
        from petrova.commands.voice import listen_command
        return listen_command()

    elif primary in ("web", "search", "fetch", "repo"):
        from petrova.commands.web import web_command
        return web_command(args)



    elif primary in ("status", "info"):
        console.print()
        console.print(get_status_table())
        console.print()
        return True

    elif primary in ("stats", "telemetry", "hw", "temp"):
        from petrova.commands.stats import stats_command
        return stats_command()


    elif primary in ("version", "v"):
        return version_command()

    elif primary in ("about",):
        return about_command()

    elif primary in ("clear", "cls"):
        return clear_command()

    elif primary in ("exit", "quit", "q"):
        return exit_command()

    elif primary in ("server", "srv"):
        return server_command(args)

    elif primary in ("memory", "mem"):
        return memory_command(args)

    elif primary in ("config", "setup"):
        return config_command(args)

    elif primary in ("gui", "app", "ui", "desktop"):
        from petrova.commands.gui import gui_command
        return gui_command()


    # If it was an unrecognized slash command (starts with /), warn the user
    if trimmed.startswith("/"):
        console.print(f"[bold yellow]Unknown command:[/bold yellow] [red]{trimmed}[/red]")
        console.print("Type [green]/help[/green] to see available commands.")
        return True

    return False
