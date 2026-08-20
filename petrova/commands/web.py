"""
Web Search & Online Repository Fetch Commands (/web, /search, /fetch, /repo).
"""

from rich.panel import Panel
from rich.markdown import Markdown
from petrova.ui.console import console
from petrova.tools.web import fetch_web_page, fetch_github_repo, search_duckduckgo
from petrova.brain.brain import stream_ask


def web_command(args: list[str] = None):
    if not args:
        console.print("[yellow]Usage:[/yellow] [green]/web <search query>[/green] or [green]/fetch <url>[/green]")
        return True

    query = " ".join(args)

    if query.startswith("http://") or query.startswith("https://"):
        console.print(f"[dim]Analyzing online resource: {query}...[/dim]")
        data = fetch_web_page(query)
        if data:
            console.print(Panel(data[:1500] + ("\n\n...[truncated]" if len(data) > 1500 else ""), title="Fetched Content", border_style="cyan"))
        else:
            console.print("[red]Could not retrieve content from URL.[/red]")
        return True

    # Search web
    results = search_duckduckgo(query)
    console.print(Panel(results, title=f"Web Search: {query}", border_style="cyan"))
    return True
