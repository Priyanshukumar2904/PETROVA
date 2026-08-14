from petrova.brain.provider import ask_model
from petrova.memory.store import initialize, get_memories, save_memory
from petrova.memory.extractor import extract_memory


initialize()

conversation: list[dict[str, str]] = []

MAX_SESSION_MESSAGES = 12
MAX_MEMORIES = 10


def ask(prompt: str) -> str:
    """
    PETROVA Brain
    Maintains short-term session context and persistent local memory.
    """

    memories = get_memories(MAX_MEMORIES)

    context = []

    if memories:
        context.append({
            "role": "system",
            "content": (
                "These are persistent memories about the user or their projects. "
                "Use them only when relevant. Do not mention the memory system "
                "unless the user asks about it.\n\n"
                + "\n".join(f"- {memory}" for memory in memories)
            ),
        })

    context.extend(conversation[-MAX_SESSION_MESSAGES:])

    context.append({
        "role": "user",
        "content": prompt,
    })

    response = ask_model(context)

    conversation.append({
        "role": "user",
        "content": prompt,
    })

    conversation.append({
        "role": "assistant",
        "content": response,
    })

    memory = extract_memory(prompt)

    if memory:
        content, category, importance = memory
        save_memory(content, category, importance)

    return response