"""
Help & Available Slash Commands Table.
"""

from rich.table import Table
from petrova.ui.console import console


def help_command():
    table = Table(
        title="PETROVA Built-in Slash Commands",
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("Command", style="bold green", width=22)
    table.add_column("Description")

    # General
    table.add_row("/help", "Show this command reference")
    table.add_row("/status", "Display current system, model, and memory status")
    table.add_row("/config [or /setup]", "Reconfigure user name, AI model, or backend")
    table.add_row("/clear", "Clear terminal screen")
    table.add_row("/exit [or /quit]", "Exit PETROVA session")

    # Server Management
    table.add_row("/server status", "Check status of the local AI inference server")
    table.add_row("/server start", "Start the local AI inference server (llama-server/Ollama)")
    table.add_row("/server stop", "Stop the active local AI server process")

    # Memory Management
    table.add_row("/memory list", "View all stored user facts and preferences")
    table.add_row("/memory search <query>", "Search stored memories by keyword")
    table.add_row("/memory add <fact>", "Manually store a new memory item")
    table.add_row("/memory delete <id>", "Delete a memory entry by its ID number")
    table.add_row("/memory clear", "Wipe all stored memories (with confirmation)")

    console.print()
    console.print(table)
    console.print()
    return True
