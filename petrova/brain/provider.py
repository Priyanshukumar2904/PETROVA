import requests

SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"

SYSTEM_PROMPT = """
You are PETROVA.

PETROVA is a privacy-first AI operating assistant for Linux.

You are concise, technically accurate, and helpful.

If asked about Linux, programming, cybersecurity, or system administration,
provide practical answers.

Never claim to perform actions you have not actually performed.
"""


def ask_model(messages: list[dict[str, str]]) -> str:
    response = requests.post(
        SERVER_URL,
        json={
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *messages,
            ],
            "temperature": 0.7,
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()