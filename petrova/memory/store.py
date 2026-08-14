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

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO memories
            (content, category, importance)
            VALUES (?, ?, ?)
            """,
            (content.strip(), category, importance),
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


def delete_memory(content: str):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "DELETE FROM memories WHERE content = ?",
            (content,),
        )
        connection.commit()