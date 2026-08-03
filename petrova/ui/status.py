from rich.table import Table


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
    table.add_row("AI Model", "[bold yellow]OFFLINE[/bold yellow]")
    table.add_row("Memory", "[bold yellow]OFFLINE[/bold yellow]")

    return table