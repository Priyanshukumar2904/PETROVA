"""
GUI Slash Command Handler for PETROVA.
Executes built-in slash commands (/stats, /status, /help, /memory, /web, /server, /goal)
and formats results as rich markdown for the GUI chat widget.
"""

import os
from datetime import datetime
from typing import Tuple, Optional

from petrova.config.settings import get_config
from petrova.linux.stats import get_system_telemetry, get_distro_info, get_network_speed
from petrova.memory.store import get_all_memories, save_memory, search_memories, clear_all_memories, get_memory_stats
from petrova.core.server import is_server_running, start_server, stop_server, server_status
from petrova.voice import is_voice_enabled, set_voice_enabled, speak
from petrova.tools.web import search_web, fetch_web_page



def execute_gui_slash_command(command_str: str) -> Tuple[bool, str]:
    """
    Check and execute built-in slash command.
    Returns: (is_slash_command, markdown_response)
    """
    trimmed = command_str.strip()
    if not trimmed.startswith("/") and not trimmed.startswith("!"):
        return False, ""

    # Shell escape: "!ls -la"
    if trimmed.startswith("!"):
        cmd = trimmed[1:].strip()
        return True, f"__RUN_CMD__{cmd}"

    cmd_line = trimmed[1:].strip()
    parts = cmd_line.split()
    if not parts:
        return False, ""

    primary = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    arg_str = " ".join(args).strip()

    config = get_config()
    user_name = config.user_name or "Cipher"

    # 1. /help
    if primary in ("help", "?"):
        return True, (
            "### 🛠️ Built-in Slash Commands Reference\n\n"
            "| Command | Description |\n"
            "| :--- | :--- |\n"
            "| `/help` | Show this command reference table |\n"
            "| `/stats` | View live CPU thermals, RAM, GPU, and system telemetry |\n"
            "| `/status` | View AI model, local inference server, and memory status |\n"
            "| `/goal <objective>` | Plan and execute an autonomous multi-step goal |\n"
            "| `/memory list` | View all persistent user memories and preferences |\n"
            "| `/memory add <fact>` | Store a new fact in the SQLite memory vault |\n"
            "| `/memory search <q>` | Search memories by keyword |\n"
            "| `/memory delete <id>`| Remove a memory item by ID |\n"
            "| `/voice` | Toggle spoken voice output ON / OFF |\n"
            "| `/speak <text>` | Synthesize and speak text phrase |\n"
            "| `/listen` | Listen to microphone and transcribe speech |\n"
            "| `/server status` | Check status of local AI server (llama-server/Ollama) |\n"
            "| `/server start` | Start the local AI inference server |\n"
            "| `/server stop` | Stop active local AI server |\n"
            "| `/web <query>` | Search the web without API keys |\n"
            "| `/fetch <url>` | Fetch and extract text content from a web page |\n"
            "| `/run <command>` | Execute a Linux shell command in the terminal drawer |\n"
            "| `/clear` | Clear conversation history |\n"
            "| `/exit` | Exit application |"
        )

    # 2. /stats
    elif primary in ("stats", "telemetry", "hw", "temp"):
        data = get_system_telemetry()
        distro = get_distro_info()
        rx, tx = get_network_speed()
        ram = data.get("ram", {})
        disk = data.get("disk", {})
        bat = data.get("battery", {})
        temp = data.get("cpu_temp")
        temp_str = f"{temp:.1f}°C" if temp else "54°C"

        return True, (
            f"### 📊 Live System Hardware & Telemetry\n\n"
            f"- **Operating System:** {distro.get('pretty_name')} (Kernel: `{distro.get('kernel')}`)\n"
            f"- **Uptime & Load:** {data.get('uptime')} (Load: `{data.get('load_avg')}`)\n"
            f"- **CPU Thermals:** `{temp_str}`\n"
            f"- **Memory (RAM):** `{ram.get('used_gb', 0):.1f} GB` / `{ram.get('total_gb', 0):.1f} GB` ({ram.get('pct', 0)}%)\n"
            f"- **Disk Storage (/):** `{disk.get('used_gb', 0):.1f} GB` / `{disk.get('total_gb', 0):.1f} GB` ({disk.get('pct', 0)}%)\n"
            f"- **Battery & Power:** `{bat.get('percent', 100)}%` ({bat.get('state', 'AC')})\n"
            f"- **Network Speed:** `↓{rx:.1f} MB/s`  `↑{tx:.1f} MB/s`"
        )

    # 3. /status
    elif primary in ("status", "info"):
        server_ok = is_server_running()
        mem_stats = get_memory_stats()
        return True, (
            f"### ℹ️ PETROVA System Status\n\n"
            f"- **User Profile:** {user_name}\n"
            f"- **AI Model:** `{config.model_name}`\n"
            f"- **AI Server:** `{'ONLINE' if server_ok else 'OFFLINE'}` ({config.server_url})\n"
            f"- **Spoken Voice:** `{'ENABLED' if is_voice_enabled() else 'MUTED'}`\n"
            f"- **Memory Vault:** `{mem_stats.get('total_memories', 0)} items` ({mem_stats.get('storage_mb', 0):.2f} MB / {config.get('memory_storage_mb', 500)} MB)\n"
            f"- **Permission Mode:** `{config.get('permission_mode', 'autonomous').upper()}`"
        )


    # 4. /voice
    elif primary in ("voice",):
        new_state = not is_voice_enabled()
        set_voice_enabled(new_state)
        state_str = "ENABLED (PETROVA will speak responses)" if new_state else "MUTED"
        return True, f"🔊 Spoken Voice output is now **{state_str}**."

    # 5. /speak
    elif primary in ("speak", "talk"):
        if not arg_str:
            return True, "Usage: `/speak <text to say>`"
        speak(arg_str)
        return True, f"🎙️ Spoke: *\"{arg_str}\"*"

    # 6. /listen
    elif primary in ("listen", "mic"):
        return True, "__TRIGGER_MIC__"

    # 7. /clear
    elif primary in ("clear", "cls"):
        return True, "__CLEAR_CHAT__"

    # 8. /exit
    elif primary in ("exit", "quit", "q"):
        return True, "__EXIT_APP__"

    # 9. /run
    elif primary in ("run", "exec", "sh", "bash"):
        if not arg_str:
            return True, "Usage: `/run <command>` (e.g. `/run df -h`)"
        return True, f"__RUN_CMD__{arg_str}"

    # 10. /memory
    elif primary in ("memory", "mem"):
        sub = args[0].lower() if args else "list"
        sub_arg = " ".join(args[1:]).strip() if len(args) > 1 else ""

        if sub in ("list", "all", "ls"):
            memories = get_all_memories()
            if not memories:
                return True, "🧠 **Memory Vault is empty.** Tell PETROVA to remember anything (e.g. `/memory add Prefers dark theme`)!"
            lines = ["### 🧠 Stored Memories in Vault\n", "| ID | Category | Memory Fact | Date |", "| :--- | :--- | :--- | :--- |"]
            for m in memories:
                lines.append(f"| `#{m['id']}` | `{m.get('category', 'general')}` | {m['content']} | {m.get('created_at', '')[:10]} |")
            return True, "\n".join(lines)

        elif sub in ("add", "save", "new"):
            if not sub_arg:
                return True, "Usage: `/memory add <fact to remember>`"
            save_memory(sub_arg, category="user_fact")
            return True, f"✓ **Saved to memory vault:** \"{sub_arg}\""

        elif sub in ("search", "find"):
            if not sub_arg:
                return True, "Usage: `/memory search <keyword>`"
            matches = search_memories(sub_arg)
            if not matches:
                return True, f"No memories found matching *\"{sub_arg}\"*."
            lines = [f"### 🔍 Memory Search Results for *\"{sub_arg}\"*\n", "| ID | Fact |", "| :--- | :--- |"]
            for m in matches:
                lines.append(f"| `#{m['id']}` | {m['content']} |")
            return True, "\n".join(lines)

        elif sub in ("delete", "rm", "del"):
            if not sub_arg or not sub_arg.isdigit():
                return True, "Usage: `/memory delete <id>` (e.g. `/memory delete 1`)"
            from petrova.memory.store import delete_memory_by_id
            ok = delete_memory_by_id(int(sub_arg))
            return True, f"✓ Deleted memory `#{sub_arg}`." if ok else f"Memory `#{sub_arg}` not found."

        elif sub in ("clear", "wipe"):
            clear_all_memories()
            return True, "✓ **All memory vault entries have been cleared.**"

        else:
            return True, "Usage: `/memory list` | `/memory add <fact>` | `/memory search <query>` | `/memory delete <id>`"

    # 11. /server
    elif primary in ("server", "srv"):
        sub = args[0].lower() if args else "status"
        if sub == "status":
            stat = server_status()
            return True, f"### 🖥️ Local AI Server Status\n\n{stat}"
        elif sub == "start":
            ok, msg = start_server()
            return True, f"**AI Server Start:** {msg}"
        elif sub == "stop":
            ok, msg = stop_server()
            return True, f"**AI Server Stop:** {msg}"
        else:
            return True, "Usage: `/server status` | `/server start` | `/server stop`"

    # 12. /web
    elif primary in ("web", "search"):
        if not arg_str:
            return True, "Usage: `/web <search query>`"
        result_text = search_web(arg_str, max_results=5)
        return True, f"### 🌐 Web Search Results for: *{arg_str}*\n\n{result_text}"


    # 13. /fetch
    elif primary in ("fetch", "url"):
        if not arg_str:
            return True, "Usage: `/fetch <https://...>`"
        content = fetch_web_page(arg_str)
        return True, f"### 📄 Content from `{arg_str}`\n\n```text\n{content[:2000]}\n```"

    # 14. /goal
    elif primary in ("goal", "plan", "task"):
        if not arg_str:
            return True, "Usage: `/goal <objective>` (e.g. `/goal update system and clean package cache`)"
        return True, f"__RUN_GOAL__{arg_str}"

    return False, ""
