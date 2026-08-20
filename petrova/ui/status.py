"""
System Status & Component Health Table for PETROVA.
"""

import platform
from rich.table import Table
from petrova.config.settings import get_config
from petrova.core.server import is_server_running
from petrova.memory.store import get_memory_count, get_db_size_mb
from petrova.linux.stats import get_distro_info, get_cpu_temp, get_ram_usage


def get_ai_status() -> str:
    """Check live status of the configured AI inference backend."""
    config = get_config()
    host = config.get("server_host", "127.0.0.1")
    port = config.get("server_port", 8080)

    if is_server_running(host, port):
        return f"[bold green]ONLINE[/bold green] [dim]({config.backend} @ :{port})[/dim]"
    return f"[bold yellow]OFFLINE[/bold yellow] [dim](auto-starts on query)[/dim]"


def get_status_table() -> Table:
    """Generate dynamic status table reflecting real system and component states."""
    config = get_config()
    table = Table(
        show_header=False,
        box=None,
        pad_edge=False,
        expand=False,
    )

    table.add_column(style="cyan", width=18)
    table.add_column()

    mem_count = get_memory_count()
    db_size = get_db_size_mb()
    quota = config.get("memory_storage_mb", 500)
    quota_str = f"{quota} MB" if quota > 0 else "Unlimited"

    perm_mode = config.get("permission_mode", "confirm").upper()
    distro = get_distro_info()
    cpu_temp = get_cpu_temp()
    ram = get_ram_usage()
    uname = platform.uname()

    temp_str = f" • [green]{cpu_temp}°C[/green]" if cpu_temp else ""

    table.add_row("User Profile", f"[bold green]{config.user_name}[/bold green]")
    table.add_row("AI Model", f"[bold cyan]{config.model_name}[/bold cyan]")
    table.add_row("AI Server", get_ai_status())
    table.add_row("Permissions", f"[bold green]{perm_mode}[/bold green]")
    table.add_row("Memory DB", f"[bold green]READY[/bold green] [dim]({mem_count} items, {db_size}MB / {quota_str})[/dim]")
    table.add_row("Operating System", f"[bold cyan]{distro['pretty_name']}[/bold cyan] [dim](pkg: {distro['package_manager']}/{distro['aur_helper']})[/dim]")
    table.add_row("Hardware Stats", f"[dim]RAM: {ram['used_gb']}/{ram['total_gb']}GB ({ram['pct']}%){temp_str} • Kernel: {uname.release}[/dim]")

    return table
