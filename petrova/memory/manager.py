"""
Intelligent Memory Manager for PETROVA.
Extracts and persists explicit and high-value contextual facts with zero perceived latency.
"""

import re
import threading
from typing import Optional, Tuple
from petrova.memory.store import save_memory

# Regex patterns for explicit commands
EXPLICIT_PATTERNS = [
    re.compile(r"^\s*(?:petrova[\s,:-]*)?(?:please\s+)?(?:remember\s+this|remember\s+that|remember)\s*[:,-]?\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*(?:petrova[\s,:-]*)?(?:note\s+that|save\s+this|don't\s+forget\s+that|keep\s+in\s+mind\s+that)\s*[:,-]?\s*(.+)$", re.IGNORECASE),
]

# Patterns for direct user identity and configuration declarations
FACT_PATTERNS = [
    (re.compile(r"\b(?:my\s+(?:preferred|favorite|default)\s+([a-zA-Z0-9_\-]+)\s+is\s+([^\.\n]+))", re.IGNORECASE), "preference", 4),
    (re.compile(r"\b(?:i\s+(?:usually|always|prefer\s+to)\s+use\s+([^\.\n]+))", re.IGNORECASE), "preference", 4),
    (re.compile(r"\b(?:i\s+am\s+working\s+on\s+([^\.\n]+))", re.IGNORECASE), "project", 4),
    (re.compile(r"\b(?:my\s+primary\s+OS\s+is\s+([^\.\n]+))", re.IGNORECASE), "configuration", 4),
    (re.compile(r"\b(?:my\s+email\s+is\s+([^\s,]+))", re.IGNORECASE), "fact", 4),
]


def extract_explicit_memory(prompt: str) -> Optional[Tuple[str, str, int]]:
    """Check if the user explicitly commanded PETROVA to remember something."""
    for pattern in EXPLICIT_PATTERNS:
        match = pattern.match(prompt.strip())
        if match:
            fact = match.group(1).strip()
            if fact:
                category = "instruction" if "\n" in fact or "command" in fact.lower() else "preference"
                return fact, category, 5
    return None


def extract_heuristic_facts(prompt: str) -> Optional[Tuple[str, str, int]]:
    """Detect natural user statements about preferences, projects, or setup."""
    for pattern, category, importance in FACT_PATTERNS:
        match = pattern.search(prompt.strip())
        if match:
            return match.group(0).strip(), category, importance
    return None


def process_memory(prompt: str):
    """
    Process a user message for memory extraction.
    Saves memories synchronously if explicit, or runs lightweight analysis without blocking.
    """
    # 1. Check explicit memory
    explicit = extract_explicit_memory(prompt)
    if explicit:
        fact, category, importance = explicit
        save_memory(fact, category, importance)
        return

    # 2. Check heuristic declarations
    heuristic = extract_heuristic_facts(prompt)
    if heuristic:
        fact, category, importance = heuristic
        save_memory(fact, category, importance)
        return
