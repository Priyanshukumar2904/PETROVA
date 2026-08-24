"""
PETROVA /gui Slash Command Handler.
Spawns the native desktop GUI application.
"""

import sys
import os
import subprocess
import time
from petrova.ui.console import console


def gui_command() -> bool:
    """Launch the PETROVA Desktop GUI."""
    console.print("[bold cyan]🚀 Launching PETROVA Desktop GUI Application...[/bold cyan]")
    
    # Check if graphical display server is active
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        console.print("[yellow]⚠️ Warning: Neither DISPLAY nor WAYLAND_DISPLAY environment variables are set.[/yellow]")
        console.print("[dim]If running over SSH, ensure X11/Wayland forwarding is enabled (ssh -X / ssh -Y).[/dim]\n")

    try:
        # Spawn GUI as an independent detached process
        proc = subprocess.Popen(
            [sys.executable, "-m", "petrova.gui.app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            text=True,
        )

        # Brief delay to catch early crash/import errors
        time.sleep(0.3)
        poll = proc.poll()
        if poll is not None and poll != 0:
            _, stderr = proc.communicate()
            console.print(f"[bold red]❌ Failed to start GUI (Exit code {poll}):[/bold red]\n{stderr}")
            return True

        console.print("[green]✓ PETROVA Desktop App initiated successfully.[/green]\n")
        return True
    except Exception as e:
        console.print(f"[bold red]Failed to launch GUI:[/bold red] {e}")
        return True
