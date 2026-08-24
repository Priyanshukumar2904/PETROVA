"""
Safe Linux Terminal Command Execution Engine for PETROVA.
Supports interactive TUI applications, background subprocess execution, GUI bypass, and diagnostics.
"""

import os
import sys
import time
import shutil
import subprocess
from typing import Tuple, Optional
from rich.prompt import Confirm
from rich.panel import Panel
from rich.syntax import Syntax

from petrova.ui.console import console
from petrova.config.settings import get_config

INTERACTIVE_COMMANDS = [
    "htop", "top", "btop", "nvtop", "iotop", "iftop", "nmtui", "ncdu",
    "vim", "vi", "nvim", "nano", "micro", "emacs",
    "less", "more", "man", "watch", "fzf", "lazygit", "ranger", "yazi", "mc"
]

DANGEROUS_COMMANDS = [
    "rm -rf /", "mkfs", "dd if=", "shutdown", "reboot", "poweroff",
    "init 0", "init 6", ":(){ :|:& };:", "chmod -r 777 /", "chmod 777 /",
    "> /dev/sda", "> /dev/nvme", "killall -9"
]

SAFE_READONLY_COMMANDS = [
    "echo", "printf", "stat", "tree", "ls", "dir", "pwd", "uname", "whoami", "id", "uptime", "date",
    "df", "free", "cat", "head", "tail", "grep", "find", "ps", "top",
    "htop", "btop", "neofetch", "fastfetch", "lscpu", "lsblk", "ip", "ifconfig",
    "ping", "curl", "which", "whereis", "file", "systemctl status", "sensors", "checkupdates"
]


def is_interactive(command: str) -> bool:
    """Check if command invokes a full-screen interactive TUI or editor."""
    cmd_lower = command.strip().lower()
    cmd_parts = cmd_lower.replace("h top", "htop").split()
    if not cmd_parts:
        return False
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
    timeout: int = 600,
    bypass_confirm: bool = False,
) -> Tuple[int, str, str]:
    """
    Execute a Linux shell command safely.
    Returns: (exit_code, stdout, stderr)
    """
    command = normalize_command(command)
    config = get_config()
    perm_mode = config.get("permission_mode", "autonomous")
    is_danger = is_potentially_dangerous(command)
    is_tui = is_interactive(command)
    is_tty = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False

    # 1. READ ONLY MODE
    if perm_mode == "read_only" and not bypass_confirm:
        return 0, "[Read-Only Mode: Execution skipped]", ""

    # 2. PERMISSION / CONFIRMATION CHECK (CLI Only)
    if not bypass_confirm and perm_mode == "confirm" and is_tty:
        prompt_msg = "[bold red]Execute dangerous command?[/bold red]" if is_danger else "[cyan]Run this command?[/cyan]"
        try:
            if not Confirm.ask(prompt_msg, default=not is_danger):
                return 1, "", "Execution cancelled by user."
        except Exception:
            pass

    # 3. INTERACTIVE TUI EXECUTION
    if is_tui and is_tty:
        try:
            res = subprocess.run(command, shell=True)
            return res.returncode, "[Interactive session completed]", ""
        except Exception as e:
            return 1, "", str(e)

    # 4. STANDARD EXECUTION
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
        code = process.returncode
        return code, stdout or "", stderr or ""

    except subprocess.TimeoutExpired:
        process.kill()
        return 124, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return 1, "", str(e)
