"""
AI Server & Inference Process Supervisor for PETROVA.
Supports llama-server (GGUF), Ollama, and OpenAI-compatible backends.
"""

import time
import socket
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import requests
from petrova.config.settings import get_config, find_system_gguf_models

_process: Optional[subprocess.Popen] = None


def is_server_running(host: Optional[str] = None, port: Optional[int] = None) -> bool:
    """Check whether an AI inference server is active on the configured host & port."""
    config = get_config()
    host = host or config.get("server_host", "127.0.0.1")
    port = port or config.get("server_port", 8080)

    # 1. Quick TCP socket test
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        if sock.connect_ex((host, port)) != 0:
            return False

    # 2. HTTP health ping
    try:
        url = f"http://{host}:{port}/health" if port != 11434 else f"http://{host}:{port}/api/tags"
        res = requests.get(url, timeout=1.0)
        return res.status_code in (200, 404)  # Some servers return 404 on /health but are running
    except Exception:
        return True  # Socket connected


def resolve_model_file() -> Optional[Path]:
    """Find a valid GGUF model file on this system."""
    config = get_config()
    configured_path = config.get("model_path")

    if configured_path:
        p = Path(configured_path).expanduser().resolve()
        if p.exists() and p.is_file():
            return p

    # Auto-detect available system GGUFs
    found = find_system_gguf_models()
    if found:
        return Path(found[0]["path"])

    return None


def start_server() -> Tuple[bool, str]:
    """Start local AI server based on user configuration."""
    global _process
    config = get_config()

    host = config.get("server_host", "127.0.0.1")
    port = config.get("server_port", 8080)
    backend = config.backend

    if is_server_running(host, port):
        return True, f"AI Server is already online at http://{host}:{port}"

    # 1. LLAMA-SERVER BACKEND
    if backend == "llama-server":
        if not shutil.which("llama-server"):
            return False, "Error: 'llama-server' binary not found in PATH. Please install llama.cpp or switch to Ollama."

        model_file = resolve_model_file()
        if not model_file:
            return False, "Error: No .gguf model found. Please download a model or configure the path in /config."

        command = [
            "llama-server",
            "-m", str(model_file),
            "-ngl", "auto",
            "-np", "1",
            "--metrics",
            "--host", host,
            "--port", str(port),
        ]

        try:
            _process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait up to 5 seconds for server socket to become ready
            for _ in range(25):
                time.sleep(0.2)
                if is_server_running(host, port):
                    return True, f"llama-server successfully started on http://{host}:{port} ({model_file.stem})"

            return True, f"llama-server process spawned (PID: {_process.pid}) on port {port}."

        except Exception as e:
            return False, f"Failed to launch llama-server: {e}"

    # 2. OLLAMA BACKEND
    elif backend == "ollama":
        if not shutil.which("ollama"):
            return False, "Error: 'ollama' binary not found in PATH. Please install Ollama from https://ollama.com"

        try:
            _process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(1.0)
            return True, f"Ollama serve started on http://{host}:{port}"
        except Exception as e:
            return False, f"Failed to start Ollama: {e}"

    # 3. OPENAI / CUSTOM ENDPOINT
    else:
        return False, f"External AI endpoint at http://{host}:{port} is unreachable. Please verify the server is running."


def stop_server() -> Tuple[bool, str]:
    """Stop the managed local AI server process."""
    global _process

    if _process is not None and _process.poll() is None:
        _process.terminate()
        try:
            _process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            _process.kill()
        _process = None
        return True, "AI server process terminated."

    if not is_server_running():
        return False, "AI server is not currently running."

    return False, "AI server is running externally (not spawned by this session). Please stop it manually."


def server_status() -> str:
    """Return human-readable server status."""
    config = get_config()
    host = config.get("server_host", "127.0.0.1")
    port = config.get("server_port", 8080)
    backend = config.backend

    if is_server_running(host, port):
        return f"[bold green]ONLINE[/bold green] — {backend} active at http://{host}:{port}"
    return f"[bold yellow]OFFLINE[/bold yellow] — {backend} not responding at http://{host}:{port}"
