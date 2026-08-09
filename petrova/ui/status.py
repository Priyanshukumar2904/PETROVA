import requests
from rich.table import Table


AI_SERVER_URL = "http://127.0.0.1:8080/health"


def get_ai_status():
    try:
        response = requests.get(AI_SERVER_URL, timeout=2)
        response.raise_for_status()

        if response.json().get("status") == "ok":
            return "[bold green]ONLINE[/bold green]"

    except (requests.RequestException, ValueError):
        pass

    return "[bold yellow]OFFLINE[/bold yellow]"


def get_status_table():
    table = Table(
        show_header=False,
        box=None,
        pad_edge=False,
        expand=False,
    )

    table.add_column(style="cyan", width=18)
    table.add_column()

    table.add_row("Configuration", "[bold green]READY[/bold green]")
    table.add_row("Workspace", "[bold green]READY[/bold green]")
    table.add_row("Linux Tools", "[bold green]READY[/bold green]")
    table.add_row("AI Model", get_ai_status())
    table.add_row("Memory", "[bold yellow]OFFLINE[/bold yellow]")

    return table