"""
Exit Command for PETROVA.
"""

from petrova.ui.console import console
from petrova.config.settings import get_config


def exit_command():
    config = get_config()
    name = config.user_name
    console.print(f"\n[bold green]Goodbye, {name}. Have a productive day![/bold green]\n")
    raise SystemExit
