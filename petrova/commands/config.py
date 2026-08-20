"""
Configuration Command (/config /setup).
"""

from petrova.config.wizard import run_onboarding_wizard


def config_command():
    return run_onboarding_wizard(force=True)
