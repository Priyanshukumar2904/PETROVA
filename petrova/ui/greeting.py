"""
Dynamic, Time-Aware Greeting for PETROVA.
"""

from datetime import datetime
from petrova.config.settings import get_config


def get_greeting() -> str:
    """Generate dynamic greeting based on system time and configured user name."""
    config = get_config()
    user_name = config.user_name
    hour = datetime.now().hour

    if hour < 12:
        return f"Good Morning, {user_name}."
    elif hour < 17:
        return f"Good Afternoon, {user_name}."
    elif hour < 22:
        return f"Good Evening, {user_name}."
    else:
        return f"Good Night, {user_name}."
