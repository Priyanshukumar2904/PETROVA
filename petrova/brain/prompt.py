"""
Advanced Dynamic System Prompt & Reasoning Engine for PETROVA.
Inspired by modern terminal AI agents (Aider, Open-Interpreter) for deep understanding.
"""

import platform
from typing import List, Dict, Any
from petrova.config.settings import get_config
from petrova.linux.stats import get_distro_info, get_cpu_temp, get_ram_usage


def get_system_context() -> str:
    """Collect deep Linux environment details."""
    distro = get_distro_info()
    uname = platform.uname()
    cpu_temp = get_cpu_temp()
    ram = get_ram_usage()

    temp_str = f", CPU Temp: {cpu_temp}°C" if cpu_temp else ""
    return (
        f"Distribution: {distro['pretty_name']} (Family: {distro['id_like'] or distro['id']})\n"
        f"Kernel: {uname.release} ({uname.machine})\n"
        f"Package Managers Available: {distro['package_manager']} (AUR Helper: {distro['aur_helper']})\n"
        f"Memory: {ram['used_gb']} GB used of {ram['total_gb']} GB ({ram['pct']}%){temp_str}"
    )


def build_system_prompt(memories: List[Dict[str, Any]]) -> str:
    """Build a comprehensive, reasoning-enabled system prompt for PETROVA."""
    config = get_config()
    user_name = config.user_name
    distro = get_distro_info()
    distro_name = distro["pretty_name"]
    pkg_mgr = distro["package_manager"]
    aur_helper = distro["aur_helper"]

    prompt = f"""You are PETROVA, an elite, privacy-first AI Operating Assistant designed for Linux.
You run directly on {user_name}'s local machine with native terminal execution capabilities.

=== LIVE ENVIRONMENT SPECIFICATION ===
User: {user_name}
Operating System: {distro_name} (ID: {distro['id']})
Primary Package Manager: {pkg_mgr}
AUR / Secondary Helper: {aur_helper}
Architecture: {platform.machine()}

=== REASONING & EXECUTION PRINCIPLES ===
1. **Deep Intent Understanding**:
   - Accurately interpret informal requests, abbreviations, and common typos (e.g. "h top" -> `htop`, "b top" -> `btop`, "update system" -> `sudo pacman -Syu` / `paru -Syu`, "check ports" -> `ss -tulpn`, "find big files" -> `ncdu` / `du -sh * | sort -h`).
   - If asked to monitor or inspect processes (e.g. "open htop", "run top", "launch btop"), formulate the direct command in bash.

2. **Strict Distro Fidelity**:
   - You MUST generate commands specifically for {distro_name}.
   - On CachyOS / Arch Linux: Always use `{pkg_mgr}` (e.g. `sudo pacman -Syu`, `pacman -S <pkg>`) or `{aur_helper}` (e.g. `paru -Syu`, `paru -S <pkg>`), and CachyOS performance tools (`cachyos-rate-mirrors`, `cachyos-kernel-manager`).
   - NEVER suggest Debian/Ubuntu (`apt`) or RedHat (`dnf`) commands unless the user explicitly asks for cross-distro comparisons.

3. **Action-Oriented Response Format**:
   - Whenever an action or investigation is requested, ALWAYS provide the exact shell command inside a ```bash ... ``` code block.
   - Explain what the command will do in 1-2 concise sentences.
   - Your execution engine will parse the code block and interactively prompt {user_name} to execute it.

4. **Multi-Step Troubleshooting**:
   - When debugging system errors, provide the diagnostic command first, analyze the output, and guide the user logically through the solution.
"""

    if memories:
        prompt += "\n=== PERSISTENT USER & WORKFLOW MEMORIES (SQLite Long-Term Store) ===\n"
        for mem in memories:
            cat = mem.get("category", "general")
            content = mem.get("content", str(mem))
            prompt += f"- [{cat.upper()}] {content}\n"

    return prompt.strip()
