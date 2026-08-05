from petrova.brain.provider import ask_model


def ask(prompt: str) -> str:
    """
    PETROVA Brain
    """

    return ask_model(prompt)