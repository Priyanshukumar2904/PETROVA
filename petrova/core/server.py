import socket
import subprocess
from pathlib import Path


MODEL = Path(
    "~/.cache/huggingface/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct-GGUF/"
    "snapshots/13fb94bfda8c8cf22497dc57b78f391a9acb426a/"
    "qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf"
).expanduser()

HOST = "127.0.0.1"
PORT = 8080

_process = None


def is_server_running() -> bool:
    """Check whether something is listening on the PETROVA LLM port."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((HOST, PORT)) == 0


def start_server():
    global _process

    if is_server_running():
        return "LLM server is already running."


    command = [
        "llama-server",
        "-m", str(MODEL),
        "-ngl", "auto",
        "-np", "1",
        "--metrics",
        "--host", HOST,
        "--port", str(PORT),
    ]

    _process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return f"LLM server starting on http://{HOST}:{PORT}"


def stop_server():
    global _process

    if _process is not None and _process.poll() is None:
        _process.terminate()
        _process.wait(timeout=5)
        _process = None
        return "LLM server stopped."

    if not is_server_running():
        return "LLM server is not running."

    return (
        "LLM server is running, but PETROVA did not start this process. "
        "It must currently be stopped manually."
    )


def server_status():
    if is_server_running():
        return f"LLM server is running on http://{HOST}:{PORT}"

    return "LLM server is not running."