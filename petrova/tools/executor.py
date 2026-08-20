"""
Safe Linux Terminal Command Execution Engine for PETROVA.
Supports interactive TUI applications (htop, btop, vim), live streaming, and error diagnostics.
"""

import os
import sys
import time
import subprocess
from typing import Tuple, Optional
from rich.prompt import Confirm
from rich.panel import Panel
from rich.syntax import Syntax

from petrova.ui.console import console
from petrova.config.settings import get_config

# Full-screen interactive TUI / Curses applications that require direct TTY
INTERACTIVE_COMMANDS = [
    "htop", "top", "btop", "nvtop", "iotop", "iftop", "nmtui", "ncdu",
    "vim", "vi", "nvim", "nano", "micro", "emacs",
    "less", "more", "man", "watch", "fzf", "lazygit", "ranger", "yazi", "mc"
]

# Commands considered dangerous requiring explicit warning/confirmation regardless of mode
DANGEROUS_COMMANDS = [
    "rm -rf", "rm -r", "mkfs", "dd", "shutdown", "reboot", "poweroff",
    "init 0", "init 6", ":(){ :|:& };:", "chmod -R 777", "chmod 777 /",
    "> /dev/sda", "> /dev/nvme", "killall", "pkill -9", "iptables -F"
]

# Safe read-only system inspection commands
SAFE_READONLY_COMMANDS = [
    "ls", "dir", "pwd", "uname", "whoami", "id", "uptime", "date",
    "df", "free", "cat", "head", "tail", "grep", "find", "ps", "top",
    "htop", "btop", "neofetch", "fastfetch", "lscpu", "lsblk", "ip", "ifconfig",
    "ping", "curl", "which", "whereis", "file", "systemctl status", "sensors"
]


def is_interactive(command: str) -> bool:
    """Check if command invokes a full-screen interactive TUI or editor."""
    cmd_lower = command.strip().lower()
    # Normalize typos: "h top" -> "htop", "n vim" -> "nvim"
    cmd_parts = cmd_lower.replace("h top", "htop").split()
    if not cmd_parts:
        return False
    # Check base program name (e.g. "sudo htop" -> "htop")
    base = cmd_parts[0]
    if base == "sudo" and len(cmd_parts) > 1:
        base = cmd_parts[1]
    return base in INTERACTIVE_COMMANDS


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
    if base == "sudo" and len(cmd_parts) > 1:
        base = cmd_parts[1].lower()
    return base in SAFE_READONLY_COMMANDS and not any(op in command for op in [">", ">>", "| rm", "| sh", "| bash"])


def normalize_command(command: str) -> str:
    """Normalize common user typos in command names."""
    cmd = command.strip()
    # Fix common spacing typos: "h top" -> "htop", "fast fetch" -> "fastfetch"
    replacements = {
        "h top": "htop",
        "b top": "btop",
        "n vim": "nvim",
        "fast fetch": "fastfetch",
        "neo fetch": "neofetch",
    }
    for typo, fix in replacements.items():
        if cmd.lower().startswith(typo):
            cmd = fix + cmd[len(typo):]
    return cmd


def execute_command(
    command: str,
    explanation: Optional[str] = None,
    timeout: int = 600,  # 10 minutes generous timeout for compilation & updates
) -> Tuple[int, str, str]:
    """
    Execute a Linux shell command respecting user permissions and interactive TTY needs.
    Returns: (exit_code, stdout, stderr)
    """
    command = normalize_command(command)
    config = get_config()
    perm_mode = config.get("permission_mode", "confirm")
    is_danger = is_potentially_dangerous(command)
    is_safe = is_readonly_safe(command)
    is_tui = is_interactive(command)

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

    # 3. INTERACTIVE TUI EXECUTION (htop, btop, vim, etc.)
    if is_tui:
        console.print(f"[dim]Launching interactive process: {command}...[/dim]")
        try:
            # Inherits real TTY for full-screen rendering and keyboard controls
            res = subprocess.run(command, shell=True)
            console.print(f"[dim]Interactive session ended (exit code {res.returncode}).[/dim]\n")
            return res.returncode, "[Interactive session completed]", ""
        except Exception as e:
            console.print(f"[bold red]Error running interactive tool:[/bold red] {e}")
            return 1, "", str(e)

    # 4. STANDARD LIVE OUTPUT EXECUTION
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

        # Display stdout
        if stdout:
            console.print()
            console.print(Panel(
                stdout.strip(),
                title=f"Output (exit code {code} in {duration}s)",
                border_style="green" if code == 0 else "yellow",
            ))

        # Display stderr if failed
        if stderr and code != 0:
            console.print()
            console.print(Panel(
                stderr.strip(),
                title=f"Error (exit code {code})",
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
