import requests


SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"


SYSTEM_PROMPT = """
You are PETROVA.

PETROVA is a privacy-first AI operating assistant for Linux.

You are concise, technically accurate, and helpful.

If asked about Linux, programming, cybersecurity, or system administration,
provide practical answers.

Never claim to perform actions you have not actually performed.

You have access to trusted persistent memory about the user.
When persistent memory is provided, treat it as factual context about the user.

If the user asks about information contained in persistent memory,
answer using that memory directly.

Do not say that you lack access to personal information or persistent memory
when relevant memory has been provided.

PERSISTENT MEMORY:
"""
def ask_model(messages: list[dict[str, str]]) -> str:
    system_parts = [SYSTEM_PROMPT]
    conversation = []

    for message in messages:
        if message["role"] == "system":
            system_parts.append(message["content"])
        else:
            conversation.append(message)

    response = requests.post(
        SERVER_URL,
        json={
            "messages": [
                {
                    "role": "system",
                    "content": "\n\n".join(system_parts),
                },
                *conversation,
            ],
            "temperature": 0.7,
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()