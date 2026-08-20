"""
Interactive REPL Shell for PETROVA.
Powered by prompt_toolkit for persistent history, auto-completion, and fluid UX.
"""

import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.markdown import Markdown

from petrova.brain.brain import stream_ask, ask
from petrova.core.router import route_command
from petrova.config.settings import HISTORY_FILE, get_config
from petrova.ui.console import console
from petrova.commands.exit import exit_command

# Auto-completer words
SLASH_COMMANDS = [
    "/help",
    "/status",
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

PROMPT_STYLE = Style.from_dict({
    "prompt": "#00d7d7 bold",
    "arrow": "#00ffaf bold",
})


def start_shell():
    """Run main interactive PETROVA prompt session."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    session = PromptSession(
        history=FileHistory(str(HISTORY_FILE)),
        completer=WordCompleter(SLASH_COMMANDS, ignore_case=True, match_middle=True),
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
            # Ctrl+C clears line without terminating app
            console.print()
            continue

        except EOFError:
            # Ctrl+D exits
            exit_command()
            break

        if not user_input:
            continue

        # 1. Check if user typed a built-in command
        if route_command(user_input):
            continue

        # 2. Process query with AI Brain
        console.print()
        console.print("[bold green]PETROVA[/bold green]")

        try:
            if config.get("stream_output", True):
                # Real-time token streaming
                token_buffer = []
                for token in stream_ask(user_input):
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    token_buffer.append(token)
                sys.stdout.write("\n")
                sys.stdout.flush()
            else:
                response = ask(user_input)
                console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n[dim yellow](Generation stopped by user)[/dim yellow]")
        except Exception as error:
            console.print(f"[bold red]Error:[/bold red] {error}")

        console.print()
