from rich.panel import Panel
from rich.align import Align
from .console import console

ASCII = r"""
██████╗ ███████╗████████╗██████╗  ██████╗ ██╗   ██╗ █████╗
██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗██║   ██║██╔══██╗
██████╔╝█████╗     ██║   ██████╔╝██║   ██║██║   ██║███████║
██╔═══╝ ██╔══╝     ██║   ██╔══██╗██║   ██║╚██╗ ██╔╝██╔══██║
██║     ███████╗   ██║   ██║  ██║╚██████╔╝ ╚████╔╝ ██║  ██║
╚═╝     ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝
"""

def show_banner():
    console.print(
        Panel.fit(
            ASCII,
            title="PETROVA",
            subtitle="AI Operating Assistant for Linux",
            border_style="cyan",
        )
    )
