"""
Dynamic System Prompt & System Context Builder for PETROVA.
"""

import platform
from typing import List, Dict, Any
from petrova.config.settings import get_config


def get_system_context() -> str:
    """Collect non-invasive local Linux environment details."""
    try:
        uname = platform.uname()
        os_info = f"{uname.system} ({uname.release}, {uname.machine})"
    except Exception:
        os_info = "Linux"
    return os_info


def build_system_prompt(memories: List[Dict[str, Any]]) -> str:
    """Build a comprehensive, personalized system prompt for PETROVA."""
    config = get_config()
    user_name = config.user_name
    os_info = get_system_context()

    prompt = f"""You are PETROVA, an open-source, privacy-first AI Operating Assistant for Linux.
You are running directly on the user's local machine.

Current User: {user_name}
Operating System: {os_info}

Core Directives:
1. Address the user naturally as '{user_name}'.
2. You specialize in Linux system administration, bash/shell automation, programming, and troubleshooting.
3. Be concise, technically precise, and actionable. Provide practical commands and explain them when helpful.
4. If asked to perform complex tasks, explain the recommended command or procedure clearly.
5. Never hallucinate or claim you performed system actions that you did not actually execute.
"""

    if memories:
        prompt += "\nRelevant Persistent Memories about the user (use context naturally when relevant):\n"
        for mem in memories:
            prompt += f"- {mem['content']}\n"

    return prompt.strip()
