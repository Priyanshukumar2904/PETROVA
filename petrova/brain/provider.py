"""
AI Model Provider & Streaming Client for PETROVA.
Supports OpenAI-compatible /v1/chat/completions with real-time token streaming.
"""

import json
import time
from typing import List, Dict, Any, Generator

import requests
from petrova.config.settings import get_config
from petrova.core.server import is_server_running, start_server


def get_endpoint_url() -> str:
    """Get the OpenAI-compatible chat completions endpoint."""
    config = get_config()
    host = config.get("server_host", "127.0.0.1")
    port = config.get("server_port", 8080)
    return f"http://{host}:{port}/v1/chat/completions"


def ensure_server_online() -> bool:
    """Ensure the configured AI backend is responsive, auto-starting if necessary."""
    config = get_config()
    host = config.get("server_host", "127.0.0.1")
    port = config.get("server_port", 8080)

    if is_server_running(host, port):
        return True

    if config.get("auto_start_server", True):
        ok, msg = start_server()
        if ok:
            # Poll for readiness
            for _ in range(15):
                time.sleep(0.3)
                if is_server_running(host, port):
                    return True
    return False


def stream_chat(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """
    Stream tokens in real-time from the local LLM.
    Yields individual token strings as they arrive.
    """
    config = get_config()
    model_name = config.model_name
    endpoint = get_endpoint_url()

    if not ensure_server_online():
        yield (
            f"[bold yellow]⚠️ AI Server Offline[/bold yellow]\n\n"
            f"PETROVA could not connect to the inference server at [cyan]{config.server_url}[/cyan].\n"
            f"• Type [green]/server start[/green] to launch it.\n"
            f"• Type [green]/config[/green] to reconfigure your AI model and backend."
        )
        return

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }

    try:
        with requests.post(
            endpoint,
            json=payload,
            stream=True,
            timeout=180,
        ) as response:
            if response.status_code != 200:
                yield f"[bold red]API Error ({response.status_code}):[/bold red] {response.text}"
                return

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                if line.startswith("data: "):
                    line = line[6:].strip()

                if line == "[DONE]":
                    break

                try:
                    chunk = json.loads(line)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

    except requests.exceptions.ConnectionError:
        yield (
            f"[bold red]Connection Refused:[/bold red] Could not reach AI server at {endpoint}.\n"
            f"Please verify your local backend (llama-server / Ollama) is running."
        )
    except Exception as e:
        yield f"[bold red]Error during model inference:[/bold red] {e}"


def ask_model(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
) -> str:
    """Non-streaming query helper for internal background tasks."""
    endpoint = get_endpoint_url()
    config = get_config()
    model_name = config.model_name

    if not ensure_server_online():
        return "AI server is offline."

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"
