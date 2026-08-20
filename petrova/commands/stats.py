"""
Real-time System & Hardware Telemetry Command (/stats).
Renders live CPU temperature, memory, disk, and Linux kernel diagnostics.
"""

from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from petrova.ui.console import console
from petrova.linux.stats import get_system_telemetry, get_cpu_temp, get_ram_usage, get_disk_usage, get_distro_info


def stats_command():
    """Render full hardware, thermal, and distribution dashboard."""
    telemetry = get_system_telemetry()
    distro = telemetry["distro"]
    ram = telemetry["ram"]
    disk = telemetry["disk"]
    temp = telemetry["cpu_temp"]

    table = Table(show_header=False, box=None, expand=True)
    table.add_column("Category", style="bold cyan", width=22)
    table.add_column("Details")

    # Distro & Kernel
    table.add_row("Operating System", f"[bold green]{distro['pretty_name']}[/bold green] [dim](Family: {distro['id_like'] or distro['id']})[/dim]")
    table.add_row("Linux Kernel", f"[cyan]{telemetry['kernel']}[/cyan]")
    table.add_row("Package Manager", f"[bold]{distro['package_manager']}[/bold] [dim](AUR Helper: {distro['aur_helper']})[/dim]")

    # Thermals
    if temp:
        temp_color = "green" if temp < 65 else ("yellow" if temp < 85 else "red")
        table.add_row("CPU Temperature", f"[{temp_color}]{temp}°C[/{temp_color}]")
    else:
        table.add_row("CPU Temperature", "[dim]Thermal sensors unavailable[/dim]")

    # Memory Bar
    ram_bar = "█" * int(ram["pct"] / 5) + "░" * (20 - int(ram["pct"] / 5))
    table.add_row("Memory (RAM)", f"[green]{ram['used_gb']} GB[/green] / {ram['total_gb']} GB ({ram['pct']}%) [dim][{ram_bar}][/dim]")

    # Storage Bar
    disk_bar = "█" * int(disk["pct"] / 5) + "░" * (20 - int(disk["pct"] / 5))
    table.add_row("Disk (Root /)", f"[green]{disk['used_gb']} GB[/green] / {disk['total_gb']} GB ({disk['pct']}%) [dim][{disk_bar}][/dim]")

    console.print()
    console.print(Panel(table, title="📊 System Hardware & Telemetry Dashboard", border_style="cyan"))
    console.print()
    return True
