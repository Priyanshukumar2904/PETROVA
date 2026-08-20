"""
Interactive REPL Shell for PETROVA.
Clean typography, live streaming metrics, voice synthesis, and safe command execution with auto-diagnostics.
"""

import sys
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm

from petrova.brain.brain import stream_ask, ask, extract_suggested_commands
from petrova.core.router import route_command
from petrova.tools.executor import execute_command
from petrova.config.settings import HISTORY_FILE, get_config
from petrova.linux.stats import get_cpu_temp, get_ram_usage
from petrova.voice import is_voice_enabled, speak
from petrova.ui.console import console
from petrova.commands.exit import exit_command

# Built-in Slash Commands for Tab completion
SLASH_COMMANDS = [
    "/help",
    "/goal",
    "/voice",
    "/voice on",
    "/voice off",
    "/voice loop",
    "/listen",
    "/speak",
    "/stats",
    "/status",
    "/run",
    "/web",
    "/fetch",
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

# Clean terminal style definitions
PROMPT_STYLE = Style.from_dict({
    "prompt": "#00d7d7 bold",
    "arrow": "#00ffaf bold",
    "completion-menu": "bg:#202020 #00ffff",
    "completion-menu.completion": "bg:#202020 #cccccc",
    "completion-menu.completion.current": "bg:#008080 #ffffff bold",
})


def handle_suggested_commands(full_response: str):
    """Detect shell commands proposed by PETROVA, offer execution and auto-diagnostics on failure."""
    config = get_config()
    perm_mode = config.get("permission_mode", "confirm")

    if perm_mode == "read_only":
        return

    commands = extract_suggested_commands(full_response)
    if not commands:
        return

    for cmd in commands[:2]:
        console.print()
        console.print(Panel(
            Syntax(cmd, "bash", theme="monokai", line_numbers=False),
            title="⚡ Proposed System Command",
            subtitle=f"Permission Mode: {perm_mode.upper()}",
            border_style="cyan",
        ))

        # Execute using permission rules in executor
        code, stdout, stderr = execute_command(cmd)

        # Auto-diagnosis hook on non-zero exit codes (except user cancellation)
        if code not in (0, 1) and stderr:
            console.print()
            if Confirm.ask("[bold yellow]Command encountered an error. Ask PETROVA to diagnose & fix?[/bold yellow]", default=True):
                console.print("\n[bold green]PETROVA (Diagnosis)[/bold green]")
                diag_prompt = f"The command `{cmd}` failed with exit code {code}.\nError details:\n{stderr}\nPlease diagnose the root cause and provide the corrected command."
                diag_parts = []
                for token in stream_ask(diag_prompt):
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    diag_parts.append(token)
                sys.stdout.write("\n")
                sys.stdout.flush()
                if is_voice_enabled():
                    speak("".join(diag_parts))


def start_shell():
    """Run main interactive PETROVA prompt session."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

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
            # Ctrl+C clears the current line
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
        token_count = 0
        start_time = time.time()

        try:
            # Real-time token streaming
            for token in stream_ask(user_input):
                sys.stdout.write(token)
                sys.stdout.flush()
                full_response_parts.append(token)
                token_count += 1
            sys.stdout.write("\n")
            sys.stdout.flush()

            duration = round(time.time() - start_time, 2)
            full_response = "".join(full_response_parts)

            # Telemetry metrics bar
            if token_count > 0 and duration > 0:
                tps = round(token_count / duration, 1)
                temp = get_cpu_temp()
                ram = get_ram_usage()
                temp_str = f" • 🌡️ {temp}°C" if temp else ""
                console.print(
                    f"[dim]⏱️ {duration}s  •  ⚡ {tps} tok/s  •  🪙 ~{token_count} tokens{temp_str}  •  🧠 RAM: {ram['used_gb']}GB[/dim]"
                )

            # Speak response if voice output is enabled
            if is_voice_enabled():
                speak(full_response)

            # 3. Check if response proposed terminal commands to run
            handle_suggested_commands(full_response)

        except KeyboardInterrupt:
            console.print("\n[dim yellow](Generation stopped by user)[/dim yellow]")
        except Exception as error:
            console.print(f"[bold red]Error:[/bold red] {error}")

        console.print()
