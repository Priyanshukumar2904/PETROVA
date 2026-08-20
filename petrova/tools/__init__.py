"""
PETROVA Tools Subsystem.
"""
from petrova.tools.executor import execute_command, is_potentially_dangerous, is_readonly_safe
from petrova.tools.web import fetch_web_page, fetch_github_repo, search_duckduckgo

__all__ = [
    "execute_command",
    "is_potentially_dangerous",
    "is_readonly_safe",
    "fetch_web_page",
    "fetch_github_repo",
    "search_duckduckgo",
]
