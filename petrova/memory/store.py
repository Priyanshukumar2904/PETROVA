import re
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "petrova.db"


def initialize():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL DEFAULT 'general',
                importance INTEGER NOT NULL DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def save_memory(
    content: str,
    category: str = "general",
    importance: int = 3,
):
    importance = max(1, min(5, importance))
    content = content.strip()

    if not content:
        return

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO memories
            (content, category, importance)
            VALUES (?, ?, ?)
            """,
            (content, category, importance),
        )
        connection.commit()


def get_memories(limit: int = 10) -> list[str]:
    with sqlite3.connect(DB_PATH) as connection:
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


def search_memories(query: str, limit: int = 5) -> list[dict]:
    """
    Return memories ranked by simple local text relevance.

    This is intentionally model-free. It gives PETROVA a lightweight
    retrieval layer that we can later upgrade to embeddings.
    """

    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z0-9_]+", query)
        if len(word) >= 3
    }

    if not words:
        return []

    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT id, content, category, importance
            FROM memories
            """
        ).fetchall()

    results = []

    for memory_id, content, category, importance in rows:
        text = content.lower()

        score = sum(
            1
            for word in words
            if word in text
        )

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


def delete_memory(content: str):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "DELETE FROM memories WHERE content = ?",
            (content,),
        )
        connection.commit()