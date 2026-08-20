"""
Intelligent Memory Decision & Privacy Filtering Engine for PETROVA.
Distinguishes high-value persistent facts from ephemeral chit-chat and sensitive secrets.
"""

import re
from typing import Tuple, Optional

# Patterns to strictly IGNORE (ephemeral, trivial, or noise)
EPHEMERAL_PATTERNS = [
    re.compile(r"^\s*(?:hi|hello|hey|yo|howdy|good\s+(?:morning|afternoon|evening|night)|greetings)[\s!.]*$", re.IGNORECASE),
    re.compile(r"^\s*(?:thanks|thank\s+you|thx|ok|okay|cool|nice|great|got\s+it|understood|awesome|bye|goodbye|cya)[\s!.]*$", re.IGNORECASE),
    re.compile(r"^\s*(?:what\s+is\s+the\s+time|what\s+time|what\s+is\s+today's\s+date|what\s+day)[\s?]*$", re.IGNORECASE),
    re.compile(r"^\s*(?:who\s+are\s+you|what\s+is\s+your\s+name|what\s+can\s+you\s+do)[\s?]*$", re.IGNORECASE),
    re.compile(r"^\s*(?:ping|test|echo\s+.*)[\s.]*$", re.IGNORECASE),
]

# Sensitive patterns (tokens, passwords, private keys - never store in plain text memory!)
SECRET_PATTERNS = [
    re.compile(r"(?:password|passwd|secret|api_key|token|auth)\s*[:=]\s*['\"]?[^\s'\"]+", re.IGNORECASE),
    re.compile(r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"),
    re.compile(r"ghp_[A-Za-z0-9_]{36}"),
    re.compile(r"bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
]

# Explicit memory commands
EXPLICIT_TRIGGERS = [
    re.compile(r"^\s*(?:petrova[\s,:-]*)?(?:please\s+)?(?:remember\s+this|remember\s+that|remember)\s*[:,-]?\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*(?:petrova[\s,:-]*)?(?:note\s+that|save\s+this|don't\s+forget\s+that|keep\s+in\s+mind\s+that)\s*[:,-]?\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*(?:petrova[\s,:-]*)?(?:add\s+to\s+memory|memorize)\s*[:,-]?\s*(.+)$", re.IGNORECASE),
]

# Heuristic category extractors
KNOWLEDGE_PATTERNS = [
    (re.compile(r"\b(?:my\s+(?:preferred|favorite|default)\s+([a-zA-Z0-9_\-]+)\s+is\s+([^\.\n]+))", re.IGNORECASE), "preference", 4),
    (re.compile(r"\b(?:i\s+(?:usually|always|prefer\s+to)\s+use\s+([^\.\n]+))", re.IGNORECASE), "preference", 4),
    (re.compile(r"\b(?:i\s+am\s+(?:working\s+on|building|developing)\s+([^\.\n]+))", re.IGNORECASE), "project", 4),
    (re.compile(r"\b(?:my\s+project\s+(?:is\s+called|name\s+is|is)\s+([^\.\n]+))", re.IGNORECASE), "project", 4),
    (re.compile(r"\b(?:my\s+(?:primary|main)\s+(?:os|distro|workstation|laptop)\s+is\s+([^\.\n]+))", re.IGNORECASE), "configuration", 4),
    (re.compile(r"\b(?:my\s+(?:cpu|gpu|ram|disk)\s+is\s+([^\.\n]+))", re.IGNORECASE), "configuration", 3),
    (re.compile(r"\b(?:i\s+live\s+in\s+([^\.\n]+)|my\s+timezone\s+is\s+([^\.\n]+))", re.IGNORECASE), "fact", 3),
    (re.compile(r"\b(?:my\s+name\s+is\s+([^\.\n]+)|call\s+me\s+([^\.\n]+))", re.IGNORECASE), "identity", 5),
]


def is_sensitive(text: str) -> bool:
    """Detect if text contains sensitive credentials or secret keys."""
    return any(p.search(text) for p in SECRET_PATTERNS)


def is_ephemeral(text: str) -> bool:
    """Detect if text is casual banter or transient lookup."""
    return any(p.match(text) for p in EPHEMERAL_PATTERNS)


def evaluate_memory_candidate(user_prompt: str) -> Tuple[bool, str, int, str]:
    """
    Intelligent decision engine: evaluates whether user input contains
    information worth saving to persistent long-term storage.

    Returns: (should_remember, category, importance_1_to_5, memory_text)
    """
    trimmed = user_prompt.strip()

    # 1. Privacy Check: Discard credentials immediately
    if is_sensitive(trimmed):
        return False, "ignored", 0, ""

    # 2. Ephemeral Check: Discard casual banter / greetings
    if is_ephemeral(trimmed):
        return False, "ephemeral", 0, ""

    # 3. Explicit Directives (User command to remember)
    for pattern in EXPLICIT_TRIGGERS:
        match = pattern.match(trimmed)
        if match:
            content = match.group(1).strip()
            if content and not is_sensitive(content):
                category = "instruction" if ("\n" in content or "command" in content.lower()) else "preference"
                return True, category, 5, content

    # 4. Heuristic Declarations (Natural facts about user, system, or project)
    for pattern, category, importance in KNOWLEDGE_PATTERNS:
        match = pattern.search(trimmed)
        if match:
            content = match.group(0).strip()
            if content and not is_sensitive(content):
                return True, category, importance, content

    # 5. Default: Ignore ordinary questions & transient interactions
    return False, "transient", 0, ""
