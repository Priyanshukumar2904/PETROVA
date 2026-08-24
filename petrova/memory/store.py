"""
Persistent SQLite Memory Storage for PETROVA with Storage Quota Enforcement.
Stores user facts, preferences, workflows, and episodic session journals.
"""

import os
import re
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from petrova.config.settings import DB_FILE, get_config


@contextmanager
def get_db():
    """Context manager for SQLite database connection that guarantees cleanup."""
    connection = sqlite3.connect(DB_FILE)
    try:
        yield connection
    finally:
        connection.close()


def initialize():
    """Initialize memory database and table schemas."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with get_db() as connection:
        # Long-term semantic facts
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL DEFAULT 'general',
                importance INTEGER NOT NULL DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_category ON memories (category)"
        )

        # Episodic session logs for conversational continuity
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                commands_run INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def get_db_size_mb() -> float:
    """Return database file size in megabytes."""
    if DB_FILE.exists():
        return round(DB_FILE.stat().st_size / (1024 * 1024), 2)
    return 0.0


def enforce_storage_quota():
    """Prune lowest-priority old memories if storage quota is exceeded."""
    config = get_config()
    max_mb = config.get("memory_storage_mb", 500)
    
    if max_mb <= 0:
        return

    current_mb = get_db_size_mb()
    if current_mb > max_mb:
        with get_db() as connection:
            connection.execute(
                """
                DELETE FROM memories
                WHERE id IN (
                    SELECT id FROM memories
                    WHERE importance <= 2
                    ORDER BY id ASC
                    LIMIT 200
                )
                """
            )
            connection.commit()
            connection.execute("VACUUM")


def save_memory(
    content: str,
    category: str = "general",
    importance: int = 3,
) -> bool:
    """Save or update a memory in persistent storage."""
    importance = max(1, min(5, importance))
    content = content.strip()

    if not content:
        return False

    initialize()
    enforce_storage_quota()

    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO memories (content, category, importance)
            VALUES (?, ?, ?)
            ON CONFLICT(content) DO UPDATE SET
                category = excluded.category,
                importance = excluded.importance,
                updated_at = CURRENT_TIMESTAMP
            """,
            (content, category.lower(), importance),
        )
        connection.commit()
        return cursor.rowcount > 0


def log_session_summary(summary: str, commands_run: int = 0):
    """Record summary of session activities for continuity on next launch."""
    initialize()
    with get_db() as connection:
        connection.execute(
            """
            INSERT INTO session_logs (summary, commands_run)
            VALUES (?, ?)
            """,
            (summary.strip(), commands_run),
        )
        connection.commit()


def get_last_session_summary() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent session summary."""
    initialize()
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT summary, commands_run, created_at
            FROM session_logs
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    if row:
        return {
            "summary": row[0],
            "commands_run": row[1],
            "created_at": row[2],
        }
    return None


def get_memories(limit: int = 10) -> List[str]:
    """Get top memories ordered by importance and recency."""
    initialize()
    with get_db() as connection:
        rows = connection.execute(
            """
            SELECT content
            FROM memories
            ORDER BY importance DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [row[0] for row in rows]


def get_all_memories(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all stored memories as dictionaries."""
    initialize()
    with get_db() as connection:
        if category:
            rows = connection.execute(
                """
                SELECT id, content, category, importance, created_at
                FROM memories
                WHERE category = ?
                ORDER BY importance DESC, id DESC
                """,
                (category.lower(),),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, content, category, importance, created_at
                FROM memories
                ORDER BY importance DESC, id DESC
                """
            ).fetchall()

    return [
        {
            "id": r[0],
            "content": r[1],
            "category": r[2],
            "importance": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]


def search_memories(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Return memories ranked by fast local text relevance and importance.
    """
    initialize()
    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z0-9_]+", query)
        if len(word) >= 2
    }

    if not words:
        return []

    with get_db() as connection:
        rows = connection.execute(
            """
            SELECT id, content, category, importance
            FROM memories
            """
        ).fetchall()

    results = []

    for memory_id, content, category, importance in rows:
        text = content.lower()
        score = sum(1 for word in words if word in text)

        if score == 0:
            continue

        results.append({
            "id": memory_id,
            "content": content,
            "category": category,
            "importance": importance,
            "score": score,
        })

    results.sort(
        key=lambda memory: (
            memory["score"],
            memory["importance"],
            memory["id"],
        ),
        reverse=True,
    )

    return results[:limit]


def delete_memory_by_id(memory_id: int) -> bool:
    """Delete a memory entry by ID."""
    initialize()
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        connection.commit()
        return cursor.rowcount > 0


def delete_memory(content: str) -> bool:
    """Delete a memory entry by matching content string."""
    initialize()
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM memories WHERE content = ?", (content,))
        connection.commit()
        return cursor.rowcount > 0


def clear_all_memories() -> int:
    """Delete all memories from database."""
    initialize()
    with get_db() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM memories")
        connection.commit()
        return cursor.rowcount


def get_memory_count() -> int:
    """Get the total count of stored memories."""
    initialize()
    with get_db() as connection:
        row = connection.execute("SELECT COUNT(*) FROM memories").fetchone()
        return row[0] if row else 0


def get_memory_stats() -> Dict[str, Any]:
    """Return memory count and database storage stats."""
    return {
        "total_memories": get_memory_count(),
        "storage_mb": get_db_size_mb(),
    }

