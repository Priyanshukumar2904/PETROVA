from datetime import datetime


def get_greeting() -> str:
    hour = datetime.now().hour

    if hour < 12:
        return "Good Morning, Cipher."

    if hour < 17:
        return "Good Afternoon, Cipher."

    if hour < 22:
        return "Good Evening, Cipher."

    return "Good Night, Cipher."
