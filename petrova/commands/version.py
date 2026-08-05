from rich.panel import Panel

from petrova.ui.console import console

VERSION = "0.1.0"
CODENAME = "Genesis"


def version_command():
    console.print()

    console.print(
        Panel.fit(
            f"[bold cyan]PETROVA[/bold cyan]\n\n"
            f"Version  : {VERSION}\n"
            f"Codename : {CODENAME}",
            title="Version Information",
            border_style="cyan",
        )
    )

    return True