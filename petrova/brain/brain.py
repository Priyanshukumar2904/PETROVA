from petrova.brain.provider import ask_model
from petrova.memory.store import initialize, search_memories
from petrova.memory.manager import process_memory


initialize()

conversation: list[dict[str, str]] = []

MAX_SESSION_MESSAGES = 12
MAX_RELEVANT_MEMORIES = 5


def ask(prompt: str) -> str:
    """
    PETROVA Brain.

    Maintains short-term conversation context and retrieves only
    memories relevant to the current request.
    """

    memories = search_memories(prompt, MAX_RELEVANT_MEMORIES)

    context = []

    if memories:
        context.append({
            "role": "system",
            "content": (
                "These are relevant persistent memories about the user. "
                "Use them when relevant. Do not mention the memory system "
                "unless the user asks about it.\n\n"
                + "\n".join(
                    f"- {memory['content']}"
                    for memory in memories
                )
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

    process_memory(prompt)

    return response