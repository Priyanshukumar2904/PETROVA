from rich.panel import Panel

from petrova.ui.console import console


def about_command():
    console.print()

    console.print(
        Panel.fit(
            "[bold cyan]PETROVA[/bold cyan]\n\n"
            "Privacy-first AI Operating Assistant for Linux.\n\n"
            "Developed by Priyanshu Kumar.",
            title="About",
            border_style="cyan",
        )
    )

    return True