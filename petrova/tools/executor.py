"""
Safe Linux Terminal Command Execution Engine for PETROVA.
Implements permission checking, timeout protection, output formatting, and explain-before-execute.
"""

import time
import subprocess
from typing import Tuple, Optional
from rich.prompt import Confirm
from rich.panel import Panel
from rich.syntax import Syntax

from petrova.ui.console import console
from petrova.config.settings import get_config

# Commands considered dangerous requiring explicit warning/confirmation regardless of mode
DANGEROUS_COMMANDS = [
    "rm -rf", "rm -r", "mkfs", "dd", "shutdown", "reboot", "poweroff",
    "init 0", "init 6", ":(){ :|:& };:", "chmod -R 777", "chmod 777 /",
    "> /dev/sda", "> /dev/nvme", "killall", "pkill -9", "iptables -F"
]

SAFE_READONLY_COMMANDS = [
    "ls", "dir", "pwd", "uname", "whoami", "id", "uptime", "date",
    "df", "free", "cat", "head", "tail", "grep", "find", "ps", "top",
    "htop", "neofetch", "fastfetch", "lscpu", "lsblk", "ip", "ifconfig",
    "ping", "curl", "which", "whereis", "file", "systemctl status"
]


def is_potentially_dangerous(command: str) -> bool:
    """Check if command matches dangerous patterns."""
    cmd_lower = command.strip().lower()
    return any(danger in cmd_lower for danger in DANGEROUS_COMMANDS)


def is_readonly_safe(command: str) -> bool:
    """Check if command is a safe read-only system inspection."""
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return False
    base = cmd_parts[0].lower()
    return base in SAFE_READONLY_COMMANDS and not any(op in command for op in [">", ">>", "| rm", "| sh", "| bash"])


def execute_command(
    command: str,
    explanation: Optional[str] = None,
    timeout: int = 30,
) -> Tuple[int, str, str]:
    """
    Execute a Linux shell command respecting user permissions.
    Returns: (exit_code, stdout, stderr)
    """
    config = get_config()
    perm_mode = config.get("permission_mode", "confirm")  # "confirm", "autonomous", "read_only"
    is_danger = is_potentially_dangerous(command)
    is_safe = is_readonly_safe(command)

    # 1. READ ONLY MODE
    if perm_mode == "read_only":
        console.print()
        console.print(Panel(
            Syntax(command, "bash", theme="monokai", line_numbers=False),
            title="Suggested Command (Read-Only Mode)",
            subtitle="Copy and run in terminal manually",
            border_style="yellow",
        ))
        if explanation:
            console.print(f"[dim]{explanation}[/dim]")
        return 0, "[Read-Only Mode: Execution skipped]", ""

    # 2. PERMISSION / CONFIRMATION CHECK
    need_confirm = True
    if perm_mode == "autonomous" and is_safe and not is_danger:
        need_confirm = False

    if need_confirm:
        console.print()
        panel_title = "⚠️ High-Risk Action" if is_danger else "Terminal Command Execution"
        border = "red" if is_danger else "cyan"

        console.print(Panel(
            Syntax(command, "bash", theme="monokai", line_numbers=False),
            title=panel_title,
            border_style=border,
        ))
        if explanation:
            console.print(f"[dim]Purpose: {explanation}[/dim]")

        prompt_msg = "[bold red]Execute dangerous command?[/bold red]" if is_danger else "[cyan]Run this command?[/cyan]"
        if not Confirm.ask(prompt_msg, default=not is_danger):
            console.print("[dim]Command execution cancelled.[/dim]\n")
            return 1, "", "Execution cancelled by user."

    # 3. ACTUAL EXECUTION
    console.print(f"[dim]Running: {command}...[/dim]")
    start_time = time.time()

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = process.communicate(timeout=timeout)
        duration = round(time.time() - start_time, 2)
        code = process.returncode

        # Display output
        if stdout:
            console.print()
            console.print(Panel(
                stdout.strip(),
                title=f"Output (code {code} in {duration}s)",
                border_style="green" if code == 0 else "yellow",
            ))

        if stderr and code != 0:
            console.print()
            console.print(Panel(
                stderr.strip(),
                title=f"Error (code {code})",
                border_style="red",
            ))

        return code, stdout, stderr

    except subprocess.TimeoutExpired:
        process.kill()
        console.print(f"[bold red]Command timed out after {timeout} seconds.[/bold red]")
        return 124, "", f"Timed out after {timeout}s"
    except Exception as e:
        console.print(f"[bold red]Execution error:[/bold red] {e}")
        return 1, "", str(e)
