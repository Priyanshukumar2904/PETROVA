"""
Dynamic System Prompt & Context Builder for PETROVA.
Injects real distro identity, package managers, and hardware context for precision command formulation.
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
    """Build a comprehensive, distro-aware system prompt for PETROVA."""
    config = get_config()
    user_name = config.user_name
    distro = get_distro_info()
    distro_name = distro["pretty_name"]
    pkg_mgr = distro["package_manager"]
    aur_helper = distro["aur_helper"]

    prompt = f"""You are PETROVA, an intelligent, privacy-first AI Operating Assistant for Linux.
You are running directly on {user_name}'s local machine.

=== LIVE SYSTEM ENVIRONMENT ===
User: {user_name}
Operating System: {distro_name} (ID: {distro['id']})
Primary Package Manager: {pkg_mgr}
AUR / Secondary Helper: {aur_helper}
System Architecture: {platform.machine()}

=== CRITICAL DISTRO-SPECIFIC DIRECTIVES ===
1. You MUST tailor all terminal commands specifically for {distro_name}.
   - On CachyOS / Arch Linux: Use `{pkg_mgr}` (e.g. `sudo pacman -Syu`, `pacman -S <pkg>`) or `{aur_helper}` (e.g. `paru -Syu`, `paru -S <pkg>`), and CachyOS utilities (`cachyos-rate-mirrors`, `cachyos-kernel-manager`).
   - NEVER provide commands for foreign Linux distributions (e.g. do not suggest `apt`, `dnf`, or `zypper` unless explicitly asked).
2. When the user asks you to perform an operation (e.g. update system, install packages, check disk/RAM, inspect ports, clean cache), ALWAYS provide the precise bash command inside a ```bash ... ``` code block.
3. Your execution engine will automatically parse your bash block and offer to run it for {user_name} on their terminal.
4. Think and reason step-by-step about what the user needs on their specific system before providing the command.
5. If the user tells you a preference or fact about their workflow (e.g. "I use CachyOS with btrfs"), remember and honor it across all responses.
"""

    if memories:
        prompt += "\n=== PERSISTENT USER MEMORIES (SQLite Long-Term Store) ===\n"
        for mem in memories:
            cat = mem.get("category", "general")
            content = mem.get("content", str(mem))
            prompt += f"- [{cat.upper()}] {content}\n"

    return prompt.strip()

