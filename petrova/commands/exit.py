"""
Exit Command for PETROVA with Automatic Session Journaling.
"""

from petrova.ui.console import console
from petrova.config.settings import get_config
from petrova.linux.workspace import get_workspace_context
from petrova.memory.store import log_session_summary


def exit_command(commands_run_count: int = 0):
    config = get_config()
    name = config.user_name
    ws = get_workspace_context()

    # Log summary for next session continuity
    summary = f"Worked in '{ws['folder_name']}' project ({ws['project_type']})"
    log_session_summary(summary, commands_run=commands_run_count)

    console.print(f"\n[bold green]Take care, {name}! See you next time.[/bold green]\n")
    raise SystemExit
