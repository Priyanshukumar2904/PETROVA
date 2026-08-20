"""
Multi-Step Agentic Goal Planner & Task Execution Engine for PETROVA.
Decomposes complex system objectives into sequenced, executable steps.
"""

import json
from typing import List, Dict, Any, Optional
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

from petrova.ui.console import console
from petrova.brain.provider import ask_model
from petrova.tools.executor import execute_command
from petrova.linux.workspace import get_workspace_context
from petrova.config.settings import get_config


def plan_goal(objective: str) -> List[Dict[str, str]]:
    """Generate a step-by-step execution plan for a complex user goal."""
    ws = get_workspace_context()
    
    prompt_messages = [
        {
            "role": "system",
            "content": (
                "You are the PETROVA Goal Planning Engine.\n"
                "Break down the user's objective into 2 to 5 clear, actionable Linux terminal steps.\n"
                "Output ONLY a valid JSON array of objects with the exact schema:\n"
                '[{"step": 1, "title": "...", "command": "...", "description": "..."}]\n'
                "Do not include any explanation or markdown around the JSON."
            )
        },
        {
            "role": "user",
            "content": f"Workspace: {ws['path']}\nObjective: {objective}"
        }
    ]

    console.print("[dim]🧠 PETROVA is analyzing objective and formulating execution plan...[/dim]")
    raw_response = ask_model(prompt_messages, temperature=0.2)

    # Clean response and extract JSON
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
    if cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    try:
        steps = json.loads(cleaned)
        if isinstance(steps, list):
            return steps
    except Exception:
        pass

    # Fallback plan if model output wasn't strictly JSON
    return [
        {
            "step": 1,
            "title": "Execute Goal Objective",
            "command": f"echo 'Objective: {objective}'",
            "description": "Perform primary task actions",
        }
    ]


def execute_goal(objective: str):
    """Plan and interactively execute a multi-step objective."""
    steps = plan_goal(objective)

    table = Table(title=f"🎯 Execution Plan: {objective}", border_style="cyan", header_style="bold cyan")
    table.add_column("Step", style="bold cyan", width=6)
    table.add_column("Task", style="bold")
    table.add_column("Command", style="green")
    table.add_column("Description", style="dim")

    for s in steps:
        table.add_row(
            str(s.get("step", 1)),
            s.get("title", ""),
            s.get("command", ""),
            s.get("description", ""),
        )

    console.print()
    console.print(table)
    console.print()

    if not Confirm.ask("[bold green]Start executing this plan?[/bold green]", default=True):
        console.print("[dim]Plan cancelled.[/dim]\n")
        return

    for i, s in enumerate(steps, 1):
        console.print(f"\n[bold cyan]Step {i}/{len(steps)}: {s.get('title')}[/bold cyan]")
        cmd = s.get("command")
        if cmd:
            code, stdout, stderr = execute_command(cmd, explanation=s.get("description"))
            if code != 0 and code != 1:
                console.print(f"[bold red]Step {i} encountered an error.[/bold red]")
                if not Confirm.ask("Continue with remaining steps?", default=False):
                    console.print("[dim]Goal execution aborted.[/dim]\n")
                    return

    console.print(Panel(f"[bold green]✓ Goal completed successfully:[/bold green] {objective}", border_style="green"))
