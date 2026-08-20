"""
Memory Processing Pipeline for PETROVA.
Extracts, categorizes, and persists high-value contextual facts with zero perceived latency.
"""

from typing import Optional, Tuple
from petrova.memory.decision import evaluate_memory_candidate
from petrova.memory.store import save_memory


def process_memory(prompt: str) -> bool:
    """
    Process a user message through the intelligent decision filter.
    Returns True if a memory was saved, False if ignored.
    """
    should_remember, category, importance, content = evaluate_memory_candidate(prompt)

    if should_remember and content:
        return save_memory(content, category, importance)

    return False
