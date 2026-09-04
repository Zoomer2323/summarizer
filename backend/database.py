"""Tiny SQLite persistence layer. No ORM on purpose -- keeps things easy to read.

A new connection is opened and closed for each call. That's the simplest
correct pattern for a small SQLite-backed app like this one (SQLite doesn't
love long-lived shared connections across threads, and FastAPI's default
threadpool means each request can land on a different thread).
"""
import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = "entries.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the entries table if it doesn't exist yet. Safe to call every startup."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                summary TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _row_to_entry(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "text": row["text"],
        "summary": row["summary"],
        "tags": json.loads(row["tags"]),
        "created_at": row["created_at"],
    }


def create_entry(text: str, summary: str, tags: list[str]) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO entries (text, summary, tags, created_at) VALUES (?, ?, ?, ?)",
            (text, summary, json.dumps(tags), created_at),
        )
        conn.commit()
        new_id = cursor.lastrowid
    finally:
        conn.close()
    return {
        "id": new_id,
        "text": text,
        "summary": summary,
        "tags": tags,
        "created_at": created_at,
    }


def list_entries() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, text, summary, tags, created_at FROM entries ORDER BY id DESC"
        ).fetchall()
    finally:
        conn.close()
    return [_row_to_entry(row) for row in rows]


def get_entry(entry_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, text, summary, tags, created_at FROM entries WHERE id = ?",
            (entry_id,),
        ).fetchone()
    finally:
        conn.close()
    return _row_to_entry(row) if row else None
