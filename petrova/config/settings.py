"""
PETROVA Configuration & Persistent Settings Manager.
Follows XDG Base Directory Specification for clean Linux integration.
"""

import os
import json
import getpass
from pathlib import Path
from typing import Dict, Any, Optional

# XDG Standard Directories
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "petrova"
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "petrova"
MODELS_DIR = DATA_DIR / "models"

CONFIG_FILE = CONFIG_DIR / "config.json"
DB_FILE = DATA_DIR / "petrova.db"
HISTORY_FILE = DATA_DIR / "history"

DEFAULT_CONFIG: Dict[str, Any] = {
    "configured": False,
    "user_name": "",
    "backend": "llama-server",  # "llama-server", "ollama", "openai"
    "model_name": "Qwen2.5-Coder-7B-Instruct",
    "model_path": "",
    "server_host": "127.0.0.1",
    "server_port": 8080,
    "auto_start_server": True,
    "stream_output": True,
    "temperature": 0.7,
    "max_context_messages": 12,
    "permission_mode": "confirm",
    "memory_storage_mb": 500,
    "theme": "cyan",
}


def find_system_gguf_models() -> list[dict[str, str]]:
    """Scan common locations for downloaded GGUF models, skipping internal blob hashes and split duplicates."""
    search_dirs = [
        MODELS_DIR,
        Path.home() / ".cache" / "huggingface" / "hub",
        Path.home() / "models",
        Path.home() / ".local" / "share" / "nomic.ai" / "GPT4All",
        Path.home() / "Downloads",
    ]

    found = []
    seen = set()

    for base_dir in search_dirs:
        if base_dir.exists():
            try:
                for gguf in base_dir.rglob("*.gguf"):
                    # Exclude raw internal blob caches
                    if "blobs" in str(gguf):
                        continue
                    # Skip secondary split parts (-00002-of-, etc.) as llama-server loads from part 1
                    if "-00002-of-" in gguf.name or "-00003-of-" in gguf.name or "-00004-of-" in gguf.name:
                        continue

                    if gguf.is_file() and gguf.name not in seen:
                        seen.add(gguf.name)
                        # Clean human name
                        name = gguf.stem.replace("-00001-of-00002", "").replace("-00001-of-00003", "").replace(".gguf", "")
                        found.append({
                            "name": name,
                            "filename": gguf.name,
                            "path": str(gguf.absolute()),
                            "size_mb": round(gguf.stat().st_size / (1024 * 1024), 1),
                        })
            except (PermissionError, OSError):
                continue

    return found



class Config:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    cfg = DEFAULT_CONFIG.copy()
                    cfg.update(loaded)
                    return cfg
            except Exception as e:
                print(f"[Warning] Failed to read config ({e}). Using defaults.")
        return DEFAULT_CONFIG.copy()

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[Error] Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()

    @property
    def is_configured(self) -> bool:
        """Returns True if the user has completed initial onboarding."""
        return bool(self.data.get("configured", False)) or bool(self.data.get("user_name"))

    @property
    def user_name(self) -> str:
        return self.data.get("user_name") or getpass.getuser().capitalize()

    @property
    def model_name(self) -> str:
        return self.data.get("model_name") or "Qwen2.5-Coder-7B-Instruct"

    @property
    def backend(self) -> str:
        return self.data.get("backend") or "llama-server"

    @property
    def server_url(self) -> str:
        host = self.data.get("server_host", "127.0.0.1")
        port = self.data.get("server_port", 8080)
        return f"http://{host}:{port}"


# Global singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
