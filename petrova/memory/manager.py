import json
import re

from petrova.brain.provider import ask_model
from petrova.memory.store import save_memory


REMEMBER_PATTERN = re.compile(
    r"^\s*(?:petrova[\s,:-]*)?(?:remember this|remember this for me)\s*:?\s*",
    re.IGNORECASE,
)


def explicit_memory(prompt: str) -> str | None:
    """Return explicitly requested memory exactly as supplied."""
    match = REMEMBER_PATTERN.match(prompt)

    if not match:
        return None

    content = prompt[match.end():]

    if not content.strip():
        return None

    return content


def automatic_decision(prompt: str) -> tuple[bool, str, int]:
    """
    Ask the local model only whether the user's message should be
    remembered and how it should be categorized.

    The user's original message remains the memory content.
    """

    decision_prompt = f"""
You are PETROVA's memory decision engine.

Decide whether this user message contains information worth remembering
across future sessions.

Remember things such as:
- preferences
- important personal facts
- ongoing project information
- useful configuration
- recurring instructions
- important commands or workflows

Do NOT remember:
- ordinary questions
- temporary requests
- explanations
- greetings
- casual conversation
- information useful only for this single response

Return ONLY valid JSON.

If it should be remembered:

{{
  "remember": true,
  "category": "preference",
  "importance": 4
}}

If it should not:

{{
  "remember": false,
  "category": "context",
  "importance": 1
}}

Allowed categories:
preference, fact, project, configuration, instruction, context, command

Importance must be an integer from 1 to 5.

USER MESSAGE:
{prompt}
"""

    try:
        raw = ask_model([
            {
                "role": "user",
                "content": decision_prompt,
            }
        ])

        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)

        decision = json.loads(raw)

    except (json.JSONDecodeError, TypeError, ValueError):
        return False, "context", 1

    remember = bool(decision.get("remember", False))

    category = str(
        decision.get("category", "context")
    ).strip().lower()

    try:
        importance = int(decision.get("importance", 3))
    except (TypeError, ValueError):
        importance = 3

    importance = max(1, min(5, importance))

    return remember, category, importance


def process_memory(prompt: str) -> bool:
    """
    Process one user message.

    Explicit remember requests are always saved exactly.
    Otherwise the AI decides whether the original message is worth saving.
    """

    explicit = explicit_memory(prompt)

    if explicit:
        save_memory(
            explicit,
            "command" if "\n" in explicit else "context",
            5,
        )
        return True

    remember, category, importance = automatic_decision(prompt)

    if not remember:
        return False

    # IMPORTANT:
    # Save the original user message, not an AI-generated summary.
    save_memory(prompt, category, importance)

    return True