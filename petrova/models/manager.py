"""
Expanded Model Tier Catalog & Auto-Download Engine for PETROVA.
Provides a comprehensive selection of coding, reasoning, and lightweight local models.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TextColumn
from petrova.config.settings import MODELS_DIR
from petrova.ui.console import console

# Comprehensive Catalog of High-Performance Open Models
MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "qwen_1.5b": {
        "category": "🚀 Lightweight (Fast / Low RAM)",
        "name": "Qwen2.5-Coder-1.5B-Instruct",
        "description": "Ultra-fast coding model (~1.1 GB RAM). Ideal for older PCs, laptops, and CPU inference.",
        "ollama_tag": "qwen2.5-coder:1.5b",
        "gguf_filename": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "approx_size_mb": 980,
    },
    "llama_3b": {
        "category": "🚀 Lightweight (Fast / Low RAM)",
        "name": "Llama-3.2-3B-Instruct",
        "description": "Meta's lightweight compact model (~2.2 GB RAM). Great general Linux assistant.",
        "ollama_tag": "llama3.2:3b",
        "gguf_filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "approx_size_mb": 2020,
    },
    "qwen_7b": {
        "category": "⚡ Standard / Balanced (Recommended ⭐)",
        "name": "Qwen2.5-Coder-7B-Instruct",
        "description": "Top-rated Linux sysadmin & programming intelligence (~4.7 GB). Best overall balance.",
        "ollama_tag": "qwen2.5-coder:7b",
        "gguf_filename": "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf",
        "approx_size_mb": 4680,
    },
    "deepseek_r1_7b": {
        "category": "⚡ Standard / Balanced (Recommended ⭐)",
        "name": "DeepSeek-R1-Distill-Qwen-7B",
        "description": "Deep reasoning & multi-step troubleshooting model (~4.7 GB). Superb for debugging.",
        "ollama_tag": "deepseek-r1:7b",
        "gguf_filename": "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        "approx_size_mb": 4680,
    },
    "llama_8b": {
        "category": "⚡ Standard / Balanced (Recommended ⭐)",
        "name": "Llama-3.1-8B-Instruct",
        "description": "Meta's flagship balanced model (~4.9 GB). Strong general knowledge and shell tasks.",
        "ollama_tag": "llama3.1:8b",
        "gguf_filename": "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "approx_size_mb": 4920,
    },
    "mistral_7b": {
        "category": "⚡ Standard / Balanced (Recommended ⭐)",
        "name": "Mistral-7B-Instruct-v0.3",
        "description": "Fast, highly capable conversational and Linux utility engine (~4.4 GB).",
        "ollama_tag": "mistral:7b",
        "gguf_filename": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "approx_size_mb": 4370,
    },
    "qwen_14b": {
        "category": "🧠 Powerhouse (High VRAM / Deep Reasoning)",
        "name": "Qwen2.5-Coder-14B-Instruct",
        "description": "Advanced coding and deep Linux architecture reasoning (~9.0 GB VRAM). Needs dedicated GPU.",
        "ollama_tag": "qwen2.5-coder:14b",
        "gguf_filename": "qwen2.5-coder-14b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-Coder-14B-Instruct-GGUF/resolve/main/qwen2.5-coder-14b-instruct-q4_k_m.gguf",
        "approx_size_mb": 9000,
    },
}


def download_gguf_model(url: str, filename: str) -> Optional[Path]:
    """Download GGUF model file with live transfer speed, progress bar, and ETA."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = MODELS_DIR / filename

    if target_path.exists() and target_path.stat().st_size > 100 * 1024 * 1024:
        console.print(f"[bold green]✓ Model file already exists on disk:[/bold green] {target_path}")
        return target_path

    console.print(f"\n[cyan]Starting download: {filename}[/cyan]")
    console.print(f"[dim]Saving directly to: {target_path}[/dim]\n")

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
            task = progress.add_task(f"Downloading {filename}", total=total_size)
            
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

        console.print(f"\n[bold green]✓ Download successful![/bold green] Model ready at {target_path}\n")
        return target_path

    except Exception as e:
        console.print(f"\n[bold red]Download error:[/bold red] {e}")
        if target_path.exists():
            target_path.unlink()
        return None


def pull_ollama_model(model_tag: str) -> bool:
    """Pull an Ollama model using the local ollama CLI."""
    if not shutil.which("ollama"):
        console.print("[bold red]Ollama binary not found in PATH.[/bold red]")
        return False

    console.print(f"\n[cyan]Pulling model '{model_tag}' via Ollama engine...[/cyan]")
    try:
        cmd = ["ollama", "pull", model_tag]
        process = subprocess.Popen(cmd)
        process.wait()
        return process.returncode == 0
    except Exception as e:
        console.print(f"[bold red]Error pulling Ollama model:[/bold red] {e}")
        return False
