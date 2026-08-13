from petrova.brain.provider import ask_model
from petrova.memory.store import initialize, get_memories, save_memory


initialize()

conversation: list[dict[str, str]] = []


def ask(prompt: str) -> str:
    """
    PETROVA Brain
    Maintains session conversation and persistent local memory.
    """

    memories = get_memories()

    context = []

    if memories:
        context.append({
            "role": "system",
            "content": (
                "These are persistent memories from previous PETROVA sessions. "
                "Use them when relevant:\n\n"
                + "\n".join(f"- {memory}" for memory in memories)
            ),
        })

    context.extend(conversation)

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

    save_memory(f"User: {prompt}")
    save_memory(f"PETROVA: {response}")

    return response