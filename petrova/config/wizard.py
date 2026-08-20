"""
Interactive First-Run & Configuration Wizard for PETROVA.
Allows users to choose their name, AI backend, model, and preferences.
"""

import getpass
import shutil
import requests
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from petrova.ui.console import console
from petrova.config.settings import get_config, find_system_gguf_models, MODELS_DIR


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
            "[bold cyan]PETROVA SETUP & INITIALIZATION[/bold cyan]\n\n"
            "Welcome! Let's personalize your AI Operating Assistant in just two quick steps.",
            border_style="cyan",
            title="Genesis Setup",
        )
    )
    console.print()

    # ---------------------------------------------------------
    # Step 1: User Name Selection
    # ---------------------------------------------------------
    default_name = config.get("user_name") or getpass.getuser().capitalize()
    console.print("[bold]Step 1: Choose Your Name[/bold]")
    console.print("[dim]How should PETROVA address you during sessions?[/dim]")
    
    user_name = Prompt.ask(
        "[cyan]Your preferred name[/cyan]",
        default=default_name,
    ).strip()

    if not user_name:
        user_name = default_name

    config.set("user_name", user_name)
    console.print(f"✓ Name set to: [bold green]{user_name}[/bold green]\n")

    # ---------------------------------------------------------
    # Step 2: AI Backend & Model Selection
    # ---------------------------------------------------------
    console.print("[bold]Step 2: Choose Your AI Model & Inference Engine[/bold]")
    console.print("[dim]PETROVA works with local offline models via llama-server, Ollama, or custom endpoints.[/dim]\n")

    # Check available local options
    gguf_files = find_system_gguf_models()
    has_llama_server = bool(shutil.which("llama-server"))
    has_ollama = bool(shutil.which("ollama"))
    ollama_models = check_ollama_models()

    options = []
    
    # 1. Option: Found GGUF models
    if gguf_files:
        for idx, g in enumerate(gguf_files[:3], 1):
            options.append({
                "type": "gguf",
                "label": f"Local GGUF: {g['name']} ({g['size_mb']} MB)",
                "backend": "llama-server",
                "model_name": g["name"],
                "model_path": g["path"],
                "port": 8080,
            })

    # 2. Option: Ollama models if any
    if ollama_models:
        for m in ollama_models[:3]:
            options.append({
                "type": "ollama",
                "label": f"Ollama Model: {m}",
                "backend": "ollama",
                "model_name": m,
                "model_path": "",
                "port": 11434,
            })
    elif has_ollama:
        options.append({
            "type": "ollama",
            "label": "Ollama (Auto-connect / qwen2.5-coder:7b)",
            "backend": "ollama",
            "model_name": "qwen2.5-coder:7b",
            "model_path": "",
            "port": 11434,
        })

    # 3. Custom GGUF path option
    options.append({
        "type": "custom_gguf",
        "label": "Specify a custom GGUF model path (llama-server)",
        "backend": "llama-server",
        "model_name": "Custom-GGUF",
        "model_path": "",
        "port": 8080,
    })

    # 4. Custom OpenAI-compatible endpoint
    options.append({
        "type": "custom_api",
        "label": "Custom OpenAI-compatible Endpoint (LM Studio / vLLM / LocalAI)",
        "backend": "openai",
        "model_name": "custom-model",
        "model_path": "",
        "port": 8080,
    })

    # Print Table of Choices
    table = Table(title="Available AI Backend Options", border_style="cyan", show_header=True)
    table.add_column("#", style="bold cyan", width=4)
    table.add_column("Engine / Model Option", style="bold")
    table.add_column("Backend", style="dim")

    for i, opt in enumerate(options, 1):
        table.add_row(str(i), opt["label"], opt["backend"])

    console.print(table)
    console.print()

    choice_str = Prompt.ask(
        "[cyan]Select an option number[/cyan]",
        choices=[str(i) for i in range(1, len(options) + 1)],
        default="1",
    )
    selected = options[int(choice_str) - 1]

    # Handle custom paths if selected
    if selected["type"] == "custom_gguf":
        custom_path = Prompt.ask("[cyan]Enter full path to .gguf model file[/cyan]").strip()
        selected["model_path"] = custom_path
        selected["model_name"] = custom_path.split("/")[-1].replace(".gguf", "")

    elif selected["type"] == "custom_api":
        endpoint = Prompt.ask("[cyan]Enter endpoint URL[/cyan]", default="http://127.0.0.1:8080").strip()
        model_id = Prompt.ask("[cyan]Enter model identifier[/cyan]", default="local-model").strip()
        selected["model_name"] = model_id
        # parse port
        if ":" in endpoint:
            try:
                selected["port"] = int(endpoint.split(":")[-1].split("/")[0])
            except Exception:
                pass

    # Save to config
    config.set("backend", selected["backend"])
    config.set("model_name", selected["model_name"])
    config.set("model_path", selected.get("model_path", ""))
    config.set("server_port", selected.get("port", 8080))
    config.set("auto_start_server", True)
    config.set("stream_output", True)

    console.print()
    console.print(
        Panel.fit(
            f"[bold green]✓ Configuration Saved Successfully![/bold green]\n\n"
            f"[bold cyan]User Name :[/bold cyan] {user_name}\n"
            f"[bold cyan]AI Backend:[/bold cyan] {selected['backend']}\n"
            f"[bold cyan]Model Name:[/bold cyan] {selected['model_name']}\n"
            f"[bold cyan]Port      :[/bold cyan] {selected.get('port', 8080)}",
            border_style="green",
            title="Ready",
        )
    )
    console.print()
    return True
