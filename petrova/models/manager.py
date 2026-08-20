"""
Model Tier Catalog & Auto-Download Engine for PETROVA.
Manages lightweight, standard, and powerhouse model presets with automated fetching.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TextColumn
from petrova.config.settings import MODELS_DIR, find_system_gguf_models
from petrova.ui.console import console

# Recommended GGUF Model Presets (Q4_K_M quantizations for optimal speed & quality)
MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "lightweight": {
        "tier": "Lightweight / Fast (1.5B - 3B)",
        "name": "Qwen2.5-Coder-1.5B-Instruct",
        "description": "Ultra-fast, low memory footprint (~1.2 GB RAM). Ideal for older PCs and CPUs.",
        "ollama_tag": "qwen2.5-coder:1.5b",
        "gguf_filename": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "approx_size_mb": 980,
    },
    "standard": {
        "tier": "Standard / Balanced (7B) — Recommended ⭐",
        "name": "Qwen2.5-Coder-7B-Instruct",
        "description": "Top-tier Linux & coding reasoning (~4.7 GB RAM/VRAM). Best overall balance.",
        "ollama_tag": "qwen2.5-coder:7b",
        "gguf_filename": "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf",
        "approx_size_mb": 4680,
    },
    "powerhouse": {
        "tier": "Powerhouse / Deep Reasoning (14B - 32B)",
        "name": "Qwen2.5-Coder-14B-Instruct",
        "description": "State-of-the-art architecture & complex automation (~9.5 GB VRAM). Needs dedicated GPU.",
        "ollama_tag": "qwen2.5-coder:14b",
        "gguf_filename": "qwen2.5-coder-14b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF/resolve/main/qwen2.5-coder-14b-instruct-q4_k_m.gguf",
        "approx_size_mb": 9300,
    }
}


def download_gguf_model(url: str, filename: str) -> Optional[Path]:
    """Download GGUF model file with a live progress bar."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = MODELS_DIR / filename

    if target_path.exists() and target_path.stat().st_size > 100 * 1024 * 1024:
        console.print(f"[bold green]✓ Model file already downloaded:[/bold green] {target_path}")
        return target_path

    console.print(f"\n[cyan]Downloading {filename} to {MODELS_DIR}...[/cyan]")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        with Progress(
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching {filename}", total=total_size)
            
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

        console.print(f"[bold green]✓ Model download complete:[/bold green] {target_path}\n")
        return target_path

    except Exception as e:
        console.print(f"[bold red]Failed to download model:[/bold red] {e}")
        if target_path.exists():
            target_path.unlink()
        return None


def pull_ollama_model(model_tag: str) -> bool:
    """Pull an Ollama model using the local ollama CLI."""
    if not shutil.which("ollama"):
        console.print("[bold red]Ollama binary not found in PATH.[/bold red]")
        return False

    console.print(f"\n[cyan]Pulling model '{model_tag}' via Ollama...[/cyan]")
    try:
        cmd = ["ollama", "pull", model_tag]
        process = subprocess.Popen(cmd)
        process.wait()
        return process.returncode == 0
    except Exception as e:
        console.print(f"[bold red]Error pulling Ollama model:[/bold red] {e}")
        return False
