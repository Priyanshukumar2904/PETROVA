"""
PETROVA Central Brain.
Maintains session context, memory augmentation, and response generation.
"""

from typing import List, Dict, Generator
from petrova.config.settings import get_config
from petrova.brain.prompt import build_system_prompt
from petrova.brain.provider import stream_chat, ask_model
from petrova.memory.store import initialize, search_memories
from petrova.memory.manager import process_memory

# Ensure DB schema is ready on import
initialize()

conversation_history: List[Dict[str, str]] = []


def clear_conversation():
    """Clear in-memory session history."""
    global conversation_history
    conversation_history.clear()


def build_context(prompt: str) -> List[Dict[str, str]]:
    """Assemble system prompt, relevant memories, and recent messages."""
    config = get_config()
    max_history = config.get("max_context_messages", 12)

    # 1. Retrieve top 5 relevant memories
    memories = search_memories(prompt, limit=5)

    # 2. System prompt with memories and user identity
    system_content = build_system_prompt(memories)

    messages = [{"role": "system", "content": system_content}]

    # 3. Append bounded session context
    messages.extend(conversation_history[-max_history:])

    # 4. Append current user message
    messages.append({"role": "user", "content": prompt})

    return messages


def stream_ask(prompt: str) -> Generator[str, None, None]:
    """
    Stream model response token-by-token and update session history.
    """
    messages = build_context(prompt)
    config = get_config()
    temperature = config.get("temperature", 0.7)

    full_response_parts = []

    for token in stream_chat(messages, temperature=temperature):
        full_response_parts.append(token)
        yield token

    full_response = "".join(full_response_parts)

    # Record in history if response was generated
    if full_response and not full_response.startswith("[bold red]"):
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": full_response})

    # Asynchronously process memory extraction
    process_memory(prompt)


def ask(prompt: str) -> str:
    """Non-streaming query helper."""
    return "".join(list(stream_ask(prompt)))
