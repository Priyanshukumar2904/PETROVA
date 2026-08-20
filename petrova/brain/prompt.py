"""
Dynamic System Prompt & System Context Builder for PETROVA.
"""

import platform
from typing import List, Dict, Any
from petrova.config.settings import get_config


def get_system_context() -> str:
    """Collect local Linux environment details."""
    try:
        uname = platform.uname()
        os_info = f"{uname.system} ({uname.release}, {uname.machine})"
    except Exception:
        os_info = "Linux"
    return os_info


def build_system_prompt(memories: List[Dict[str, Any]]) -> str:
    """Build a comprehensive, action-oriented system prompt for PETROVA."""
    config = get_config()
    user_name = config.user_name
    os_info = get_system_context()

    prompt = f"""You are PETROVA, an intelligent, privacy-first AI Operating Assistant for Linux.
You are running directly on {user_name}'s local machine.

Operating Environment: {os_info}
Active User: {user_name}

Core Capabilities & Directives:
1. Address the user naturally as '{user_name}'.
2. You specialize in Linux system administration, shell automation, programming, network diagnostics, and troubleshooting.
3. When the user asks you to perform an action or operation (e.g. update system, install software, check disk usage, list processes, inspect ports, configure services), ALWAYS formulate the precise Linux shell command in a ```bash ... ``` code block.
4. Explain what the command will do concisely before or after the code block.
5. Your execution engine will automatically parse your bash block and offer to run it for {user_name} on their terminal.
6. When answering questions with web or repository context provided to you, synthesize the information accurately and concisely.
"""

    if memories:
        prompt += "\nPersistent Memories about the user & system (incorporate naturally when relevant):\n"
        for mem in memories:
            prompt += f"- {mem['content']}\n"

    return prompt.strip()
