"""
Warm, Empathetic & Context-Aware Proactive Greeting for PETROVA.
Provides a caring health check-in, workspace awareness, and continuity from the last session.
"""

from datetime import datetime
from petrova.config.settings import get_config
from petrova.linux.stats import get_cpu_temp, get_ram_usage, get_distro_info, get_battery_status
from petrova.linux.workspace import get_workspace_context
from petrova.memory.store import get_last_session_summary


def get_greeting() -> str:
    """Generate dynamic, caring, and proactive briefing for the user."""
    config = get_config()
    user_name = config.user_name
    hour = datetime.now().hour

    # 1. Time greeting
    if hour < 12:
        salutation = f"Good morning, {user_name}!"
    elif hour < 17:
        salutation = f"Good afternoon, {user_name}!"
    elif hour < 22:
        salutation = f"Good evening, {user_name}!"
    else:
        salutation = f"Working late tonight, {user_name}?"

    # 2. Hardware health assessment
    temp = get_cpu_temp()
    ram = get_ram_usage()
    distro = get_distro_info()
    battery = get_battery_status()

    health_notes = []
    if temp and temp >= 82.0:
        health_notes.append(f"⚠️ [bold yellow]Heads-up:[/bold yellow] Your CPU is running warm at [red]{temp}°C[/red].")
    elif temp:
        health_notes.append(f"✨ Workstation is running smooth at [green]{temp}°C[/green] ({distro['pretty_name']}).")

    if ram["pct"] >= 88.0:
        health_notes.append(f"⚠️ [bold yellow]High Memory:[/bold yellow] RAM usage is at [yellow]{ram['pct']}%[/yellow] ({ram['used_gb']}/{ram['total_gb']} GB).")

    if battery["present"] and not battery["plugged_in"] and battery["percent"] is not None and battery["percent"] <= 25:
        health_notes.append(f"🔋 [bold yellow]Low Battery:[/bold yellow] Battery is at [red]{battery['percent']}%[/red] ({battery.get('time_str', 'plug in soon')}).")

    # 3. Workspace check
    ws = get_workspace_context()
    ws_note = ""
    if ws["git"]["is_git"]:
        branch = ws["git"]["branch"]
        mod = ws["git"]["modified_count"]
        dirty_str = f" with [yellow]{mod} uncommitted changes[/yellow]" if mod > 0 else " ([green]clean[/green])"
        ws_note = f"📂 [bold cyan]Workspace:[/bold cyan] Working in [bold]{ws['folder_name']}[/bold] on branch [magenta]'{branch}'[/magenta]{dirty_str}."

    # 4. Episodic memory from last session
    last_sess = get_last_session_summary()
    continuity_note = ""
    if last_sess and last_sess.get("summary"):
        continuity_note = f"💡 [dim]Last time: {last_sess['summary']}[/dim]"

    # Assemble greeting text
    lines = [f"[bold cyan]{salutation}[/bold cyan]"]
    if health_notes:
        lines.append(" ".join(health_notes))
    if ws_note:
        lines.append(ws_note)
    if continuity_note:
        lines.append(continuity_note)

    return "\n".join(lines)
