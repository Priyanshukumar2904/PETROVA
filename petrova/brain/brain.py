"""
PETROVA Central Brain.
Maintains session context, web augmentation, memory retrieval, and response generation.
"""

import re
from typing import List, Dict, Generator, Optional
from petrova.config.settings import get_config
from petrova.brain.prompt import build_system_prompt
from petrova.brain.provider import stream_chat, ask_model
from petrova.memory.store import initialize, search_memories
from petrova.memory.manager import process_memory
from petrova.tools.web import fetch_web_page

# Ensure DB schema is ready on import
initialize()

conversation_history: List[Dict[str, str]] = []


def clear_conversation():
    """Clear in-memory session history."""
    global conversation_history
    conversation_history.clear()


def extract_urls(text: str) -> List[str]:
    """Find HTTP and HTTPS URLs in text."""
    url_pattern = re.compile(r"https?://[^\s<>\"')]+")
    return url_pattern.findall(text)


def extract_suggested_commands(response: str) -> List[str]:
    """
    Extract shell commands proposed by the LLM from markdown code blocks or <command> tags.
    """
    commands = []
    
    # 1. Match ```bash or ```sh or ```shell code blocks
    code_block_pattern = re.compile(r"```(?:bash|sh|shell|zsh)\n(.*?)```", re.DOTALL | re.IGNORECASE)
    for match in code_block_pattern.findall(response):
        lines = [line.strip() for line in match.strip().split("\n") if line.strip() and not line.strip().startswith("#")]
        if lines:
            commands.append("\n".join(lines))

    # 2. Match <command>...</command> tags
    tag_pattern = re.compile(r"<command>(.*?)</command>", re.DOTALL | re.IGNORECASE)
    for match in tag_pattern.findall(response):
        cmd = match.strip()
        if cmd and cmd not in commands:
            commands.append(cmd)

    return commands


def build_context(prompt: str) -> List[Dict[str, str]]:
    """Assemble system prompt, web data, relevant memories, and recent messages."""
    config = get_config()
    max_history = config.get("max_context_messages", 12)

    # 1. Retrieve top 5 relevant memories
    memories = search_memories(prompt, limit=5)

    # 2. System prompt with memories and user identity
    system_content = build_system_prompt(memories)

    messages = [{"role": "system", "content": system_content}]

    # 3. Append bounded session context
    messages.extend(conversation_history[-max_history:])

    # 4. Check if prompt contains URLs to fetch (Web / GitHub Repo inspection)
    urls = extract_urls(prompt)
    augmented_prompt = prompt
    if urls:
        web_context_chunks = []
        for url in urls[:2]:
            content = fetch_web_page(url)
            if content:
                web_context_chunks.append(content)

        if web_context_chunks:
            augmented_prompt = (
                f"{prompt}\n\n"
                f"[Attached Online Context]:\n" + "\n---\n".join(web_context_chunks)
            )

    # 5. Append current user message
    messages.append({"role": "user", "content": augmented_prompt})

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
