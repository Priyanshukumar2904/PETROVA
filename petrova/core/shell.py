"""
Interactive REPL Shell for PETROVA.
Clean typography, tab-only auto-completion (no empty blocks), and interactive command execution.
"""

import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm

from petrova.brain.brain import stream_ask, ask, extract_suggested_commands, conversation_history
from petrova.core.router import route_command
from petrova.tools.executor import execute_command
from petrova.config.settings import HISTORY_FILE, get_config
from petrova.ui.console import console
from petrova.commands.exit import exit_command

# Built-in Slash Commands for Tab completion
SLASH_COMMANDS = [
    "/help",
    "/status",
    "/run",
    "/config",
    "/setup",
    "/server",
    "/server start",
    "/server stop",
    "/server status",
    "/memory",
    "/memory list",
    "/memory search",
    "/memory add",
    "/memory delete",
    "/memory clear",
    "/clear",
    "/exit",
    "/quit",
    "/version",
    "/about",
]

# Clean terminal style definitions (no glitchy reverse-video blocks)
PROMPT_STYLE = Style.from_dict({
    "prompt": "#00d7d7 bold",
    "arrow": "#00ffaf bold",
    "completion-menu": "bg:#202020 #00ffff",
    "completion-menu.completion": "bg:#202020 #cccccc",
    "completion-menu.completion.current": "bg:#008080 #ffffff bold",
})


def handle_suggested_commands(full_response: str):
    """Detect shell commands proposed by PETROVA and offer execution."""
    config = get_config()
    perm_mode = config.get("permission_mode", "confirm")

    if perm_mode == "read_only":
        return

    commands = extract_suggested_commands(full_response)
    if not commands:
        return

    for cmd in commands[:2]:  # Handle up to 2 commands
        console.print()
        console.print(Panel(
            Syntax(cmd, "bash", theme="monokai", line_numbers=False),
            title="⚡ Proposed System Command",
            subtitle=f"Permission Mode: {perm_mode.upper()}",
            border_style="cyan",
        ))

        # Execute using permission rules in executor
        execute_command(cmd)


def start_shell():
    """Run main interactive PETROVA prompt session."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    # complete_while_typing=False ensures no popup blocks clutter the screen while typing
    session = PromptSession(
        history=FileHistory(str(HISTORY_FILE)),
        completer=WordCompleter(SLASH_COMMANDS, ignore_case=True, match_middle=True),
        complete_while_typing=False,
        style=PROMPT_STYLE,
    )

    config = get_config()

    while True:
        try:
            user_input = session.prompt(
                [
                    ("class:prompt", "PETROVA "),
                    ("class:arrow", "❯ "),
                ]
            ).strip()

        except KeyboardInterrupt:
            # Ctrl+C clears the current line without closing session
            console.print()
            continue

        except EOFError:
            # Ctrl+D exits
            exit_command()
            break

        if not user_input:
            continue

        # 1. Check if user typed a built-in slash command or !escape
        if route_command(user_input):
            continue

        # 2. Process query with AI Brain
        console.print()
        console.print("[bold green]PETROVA[/bold green]")

        full_response_parts = []
        try:
            # Real-time token streaming
            for token in stream_ask(user_input):
                sys.stdout.write(token)
                sys.stdout.flush()
                full_response_parts.append(token)
            sys.stdout.write("\n")
            sys.stdout.flush()

            full_response = "".join(full_response_parts)

            # 3. Check if response proposed terminal commands to run
            handle_suggested_commands(full_response)

        except KeyboardInterrupt:
            console.print("\n[dim yellow](Generation stopped by user)[/dim yellow]")
        except Exception as error:
            console.print(f"[bold red]Error:[/bold red] {error}")

        console.print()
