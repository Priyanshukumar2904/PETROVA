"""
Memory Management Commands (/memory list, search, add, delete, clear).
"""

from rich.table import Table
from rich.prompt import Confirm
from petrova.ui.console import console
from petrova.memory.store import (
    get_all_memories,
    search_memories,
    save_memory,
    delete_memory_by_id,
    clear_all_memories,
    get_memory_count,
)


def memory_command(args: list[str] = None):
    if not args or args[0].lower() == "list":
        category = args[1] if args and len(args) > 1 else None
        memories = get_all_memories(category)

        if not memories:
            console.print("[yellow]No memories stored yet.[/yellow] You can tell PETROVA to remember things anytime!")
            return True

        table = Table(
            title=f"PETROVA Stored Memories ({len(memories)} total)",
            border_style="cyan",
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim", width=5)
        table.add_column("Memory Content", style="bold")
        table.add_column("Category", style="magenta", width=14)
        table.add_column("Priority", style="yellow", width=8)
        table.add_column("Saved Date", style="dim", width=19)

        for m in memories:
            stars = "★" * m["importance"]
            table.add_row(
                str(m["id"]),
                m["content"],
                m["category"],
                stars,
                str(m["created_at"])[:19],
            )

        console.print()
        console.print(table)
        console.print()
        return True

    action = args[0].lower()

    if action == "search":
        if len(args) < 2:
            console.print("[red]Usage: /memory search <query>[/red]")
            return True

        query = " ".join(args[1:])
        results = search_memories(query, limit=10)

        if not results:
            console.print(f"[yellow]No matching memories found for '{query}'.[/yellow]")
            return True

        table = Table(title=f"Memory Search Results for '{query}'", border_style="cyan")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Content", style="bold")
        table.add_column("Category", style="magenta")
        table.add_column("Score", style="green", width=7)

        for r in results:
            table.add_row(str(r["id"]), r["content"], r["category"], str(r["score"]))

        console.print()
        console.print(table)
        console.print()

    elif action == "add":
        if len(args) < 2:
            console.print("[red]Usage: /memory add <fact or preference>[/red]")
            return True
        fact = " ".join(args[1:])
        save_memory(fact, category="user_added", importance=4)
        console.print(f"[bold green]✓ Memory saved:[/bold green] \"{fact}\"")

    elif action == "delete":
        if len(args) < 2:
            console.print("[red]Usage: /memory delete <id>[/red]")
            return True
        try:
            mem_id = int(args[1])
            if delete_memory_by_id(mem_id):
                console.print(f"[bold green]✓ Memory ID {mem_id} deleted.[/bold green]")
            else:
                console.print(f"[yellow]Memory ID {mem_id} not found.[/yellow]")
        except ValueError:
            console.print("[red]Please provide a numeric memory ID.[/red]")

    elif action == "clear":
        count = get_memory_count()
        if count == 0:
            console.print("[yellow]Memory database is already empty.[/yellow]")
            return True

        if Confirm.ask(f"[bold red]Are you sure you want to delete ALL {count} memories?[/bold red]"):
            clear_all_memories()
            console.print("[bold green]✓ All memories have been cleared.[/bold green]")
        else:
            console.print("[dim]Operation cancelled.[/dim]")

    else:
        console.print(f"[red]Unknown memory subcommand '{action}'.[/red] Type [green]/help[/green] for available options.")

    return True
