"""
Interactive Setup & Onboarding Wizard for PETROVA.
Configures user identity, model sizing/download, system permissions, and memory quotas.
"""

import getpass
import shutil
import requests
from pathlib import Path
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from petrova.ui.console import console
from petrova.config.settings import get_config, find_system_gguf_models, MODELS_DIR
from petrova.models.manager import MODEL_CATALOG, download_gguf_model, pull_ollama_model


def check_ollama_models() -> list[str]:
    """Fetch list of local Ollama models if Ollama is running."""
    try:
        res = requests.get("http://127.0.0.1:11434/api/tags", timeout=1.5)
        if res.status_code == 200:
            data = res.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def run_onboarding_wizard(force: bool = False) -> bool:
    """Run interactive setup wizard to configure PETROVA."""
    config = get_config()

    if config.is_configured and not force:
        return True

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]⚡ PETROVA ONBOARDING & SETUP WIZARD[/bold cyan]\n\n"
            "Welcome! Let's configure your AI Operating Assistant for your system and preferences.",
            border_style="cyan",
            title="Genesis Setup",
        )
    )
    console.print()

    # ---------------------------------------------------------
    # Step 1: User Name Personalization
    # ---------------------------------------------------------
    default_name = config.get("user_name") or getpass.getuser().capitalize()
    console.print("[bold cyan]Step 1: Choose Your Name[/bold cyan]")
    console.print("[dim]How should PETROVA address you during operations and greetings?[/dim]")
    
    user_name = Prompt.ask(
        "[green]Your preferred name[/green]",
        default=default_name,
    ).strip() or default_name

    config.set("user_name", user_name)
    console.print(f"✓ Name set to: [bold green]{user_name}[/bold green]\n")

    # ---------------------------------------------------------
    # Step 2: Model Sizing & Inference Engine Selection
    # ---------------------------------------------------------
    console.print("[bold cyan]Step 2: Choose Your AI Model & Size Tier[/bold cyan]")
    console.print("[dim]Select a model size according to your hardware capacity and performance needs:[/dim]\n")

    system_ggufs = find_system_gguf_models()
    ollama_models = check_ollama_models()
    has_ollama = bool(shutil.which("ollama"))
    has_llama_server = bool(shutil.which("llama-server"))

    options = []

    # 1. Existing System GGUFs if any
    if system_ggufs:
        for g in system_ggufs[:2]:
            options.append({
                "type": "existing_gguf",
                "label": f"Local Disk: {g['name']} ({g['size_mb']} MB)",
                "backend": "llama-server",
                "model_name": g["name"],
                "model_path": g["path"],
                "port": 8080,
            })

    # 2. Preset Tiers (Lightweight, Standard, Powerhouse)
    for key, spec in MODEL_CATALOG.items():
        options.append({
            "type": "preset",
            "key": key,
            "label": f"{spec['tier']} — {spec['name']}",
            "description": spec["description"],
            "backend": "llama-server" if has_llama_server else "ollama",
            "model_name": spec["name"],
            "spec": spec,
            "port": 8080 if has_llama_server else 11434,
        })

    # 3. Ollama local models if running
    if ollama_models:
        for m in ollama_models[:2]:
            options.append({
                "type": "ollama_existing",
                "label": f"Ollama Model: {m}",
                "backend": "ollama",
                "model_name": m,
                "model_path": "",
                "port": 11434,
            })

    # 4. Custom GGUF File Path
    options.append({
        "type": "custom_path",
        "label": "Custom GGUF Model Path (llama-server)",
        "backend": "llama-server",
        "model_name": "custom-gguf",
        "model_path": "",
        "port": 8080,
    })

    # 5. Custom OpenAI-compatible Endpoint
    options.append({
        "type": "custom_api",
        "label": "Custom Endpoint (LM Studio / vLLM / LocalAI / Cloud)",
        "backend": "openai",
        "model_name": "custom-api-model",
        "model_path": "",
        "port": 8080,
    })

    table = Table(title="AI Model & Backend Options", border_style="cyan", show_header=True)
    table.add_column("#", style="bold cyan", width=4)
    table.add_column("Tier / Model Option", style="bold")
    table.add_column("Backend", style="dim", width=14)

    for i, opt in enumerate(options, 1):
        table.add_row(str(i), opt["label"], opt["backend"])

    console.print(table)
    console.print()

    choice_str = Prompt.ask(
        "[green]Select a model option number[/green]",
        choices=[str(i) for i in range(1, len(options) + 1)],
        default="1",
    )
    selected = options[int(choice_str) - 1]

    # Handle preset download if needed
    if selected["type"] == "preset":
        spec = selected["spec"]
        if selected["backend"] == "llama-server":
            target_file = MODELS_DIR / spec["gguf_filename"]
            # Check if model exists or download
            if not target_file.exists():
                console.print(f"\n[cyan]Model size: ~{spec['approx_size_mb']} MB. Download now?[/cyan]")
                if Confirm.ask("[green]Download model automatically?[/green]", default=True):
                    downloaded = download_gguf_model(spec["url"], spec["gguf_filename"])
                    if downloaded:
                        selected["model_path"] = str(downloaded)
                else:
                    console.print("[dim]Download skipped. You can point to an existing file in /config later.[/dim]")
            else:
                selected["model_path"] = str(target_file)
        elif selected["backend"] == "ollama":
            if Confirm.ask(f"[green]Pull Ollama model '{spec['ollama_tag']}' now?[/green]", default=True):
                pull_ollama_model(spec["ollama_tag"])

    elif selected["type"] == "custom_path":
        p = Prompt.ask("[green]Enter full path to .gguf file[/green]").strip()
        selected["model_path"] = p
        selected["model_name"] = Path(p).stem

    elif selected["type"] == "custom_api":
        endpoint = Prompt.ask("[green]Enter endpoint URL[/green]", default="http://127.0.0.1:8080").strip()
        selected["model_name"] = Prompt.ask("[green]Enter model identifier[/green]", default="local-model").strip()
        if ":" in endpoint:
            try:
                selected["port"] = int(endpoint.split(":")[-1].split("/")[0])
            except Exception:
                pass

    config.set("backend", selected["backend"])
    config.set("model_name", selected["model_name"])
    config.set("model_path", selected.get("model_path", ""))
    config.set("server_port", selected.get("port", 8080))
    console.print(f"✓ Model set to: [bold green]{selected['model_name']}[/bold green]\n")

    # ---------------------------------------------------------
    # Step 3: Critical Terminal & Execution Permissions
    # ---------------------------------------------------------
    console.print("[bold cyan]Step 3: Critical Terminal Execution Permissions[/bold cyan]")
    console.print("[dim]How should PETROVA handle terminal operations on your Linux machine?[/dim]\n")

    perm_table = Table(title="System Permission Modes", border_style="cyan", show_header=True)
    perm_table.add_column("#", style="bold cyan", width=4)
    perm_table.add_column("Permission Level", style="bold", width=26)
    perm_table.add_column("Behavior")

    perm_table.add_row("1", "Interactive (Recommended) ⭐", "Explains the command and asks for confirmation [y/N] before running.")
    perm_table.add_row("2", "Autonomous Diagnostics", "Runs safe read-only checks automatically; asks confirmation for destructive commands.")
    perm_table.add_row("3", "Read-Only / Suggest Only", "Never executes commands directly. Displays syntax for manual copy-paste.")

    console.print(perm_table)
    console.print()

    perm_choice = Prompt.ask(
        "[green]Select permission mode[/green]",
        choices=["1", "2", "3"],
        default="1",
    )
    perm_map = {"1": "confirm", "2": "autonomous", "3": "read_only"}
    config.set("permission_mode", perm_map[perm_choice])
    console.print(f"✓ Permission mode set to: [bold green]{perm_map[perm_choice].upper()}[/bold green]\n")

    # ---------------------------------------------------------
    # Step 4: Memory Storage Allocation
    # ---------------------------------------------------------
    console.print("[bold cyan]Step 4: Memory Storage Allocation[/bold cyan]")
    console.print("[dim]Choose the maximum storage budget for PETROVA's persistent memory database:[/dim]\n")

    mem_table = Table(title="Memory Storage Quota", border_style="cyan", show_header=True)
    mem_table.add_column("#", style="bold cyan", width=4)
    mem_table.add_column("Storage Budget", style="bold", width=22)
    mem_table.add_column("Capacity")

    mem_table.add_row("1", "100 MB", "Compact (~50,000 memories / facts)")
    mem_table.add_row("2", "500 MB (Standard) ⭐", "Recommended (~250,000 memories)")
    mem_table.add_row("3", "2 GB", "High-capacity persistent history")
    mem_table.add_row("4", "Unlimited", "No storage pruning limit")

    console.print(mem_table)
    console.print()

    mem_choice = Prompt.ask(
        "[green]Select memory storage budget[/green]",
        choices=["1", "2", "3", "4"],
        default="2",
    )
    quota_map = {"1": 100, "2": 500, "3": 2000, "4": 0}
    config.set("memory_storage_mb", quota_map[mem_choice])
    console.print(f"✓ Memory quota set to: [bold green]{quota_map[mem_choice] if quota_map[mem_choice] > 0 else 'Unlimited'} MB[/bold green]\n")

    # Final Summary
    console.print(
        Panel.fit(
            f"[bold green]✓ All Initial Setup Completed Successfully![/bold green]\n\n"
            f"[bold cyan]User Name  :[/bold cyan] {user_name}\n"
            f"[bold cyan]Model Tier :[/bold cyan] {selected['model_name']} ({selected['backend']})\n"
            f"[bold cyan]Permissions:[/bold cyan] {config.get('permission_mode').upper()}\n"
            f"[bold cyan]Memory Cap :[/bold cyan] {config.get('memory_storage_mb')} MB",
            border_style="green",
            title="Setup Ready",
        )
    )
    console.print()
    return True
