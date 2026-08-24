"""
Safe Linux Terminal Command Execution Engine for PETROVA.
Runs native Linux shell commands in Bash with complete user PATH and environment inheritance.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
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
    "ping", "curl", "which", "whereis", "file", "systemctl status", "sensors", "checkupdates", "pacman -Q"
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


def get_execution_env() -> dict:
    """Prepare complete execution environment with full user PATH."""
    env = os.environ.copy()
    home = str(Path.home())
    extra_paths = [
        f"{home}/.local/bin",
        f"{home}/.cargo/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/local/sbin",
        "/usr/sbin",
        "/sbin",
    ]
    current_path = env.get("PATH", "")
    for p in extra_paths:
        if p not in current_path and os.path.exists(p):
            current_path = f"{p}:{current_path}"
    env["PATH"] = current_path
    env["TERM"] = "xterm-256color"
    return env


def launch_in_terminal_emulator(command: str) -> bool:
    """Launch interactive or root command in user's GUI terminal emulator."""
    terminals = [
        ("kitty", ["kitty", "-e", "bash", "-c", f"{command}; echo; read -p 'Press Enter to close...'"]),
        ("alacritty", ["alacritty", "-e", "bash", "-c", f"{command}; echo; read -p 'Press Enter to close...'"]),
        ("konsole", ["konsole", "-e", "bash", "-c", f"{command}; echo; read -p 'Press Enter to close...'"]),
        ("gnome-terminal", ["gnome-terminal", "--", "bash", "-c", f"{command}; echo; read -p 'Press Enter to close...'"]),
        ("xfce4-terminal", ["xfce4-terminal", "-e", f"bash -c '{command}; echo; read -p \"Press Enter to close...\"'"]),
        ("xterm", ["xterm", "-e", f"bash -c '{command}; echo; read -p \"Press Enter to close...\"'"]),
    ]

    for term_name, term_cmd in terminals:
        if shutil.which(term_name):
            try:
                subprocess.Popen(term_cmd, start_new_session=True)
                return True
            except Exception:
                continue
    return False


def execute_command(
    command: str,
    explanation: Optional[str] = None,
    timeout: int = 600,
    bypass_confirm: bool = False,
) -> Tuple[int, str, str]:
    """
    Execute a Linux shell command safely in Bash with full environment inheritance.
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

    # 3. INTERACTIVE TUI EXECUTION (In real TTY or spawn emulator)
    if is_tui:
        if is_tty:
            try:
                res = subprocess.run(command, shell=True, executable="/bin/bash", env=get_execution_env())
                return res.returncode, "[Interactive session completed]", ""
            except Exception as e:
                return 1, "", str(e)
        else:
            launched = launch_in_terminal_emulator(command)
            if launched:
                return 0, f"[Launched interactive session '{command}' in terminal emulator]", ""

    # 4. STANDARD EXECUTION IN BASH
    env = get_execution_env()
    shell_bin = "/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh"

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            executable=shell_bin,
            env=env,
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
