import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = Path("data") / "history.db"

def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT,
                source_type TEXT NOT NULL,
                mode TEXT NOT NULL,
                length TEXT NOT NULL,
                model TEXT NOT NULL,
                input_chars INTEGER NOT NULL,
                summary TEXT NOT NULL
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON summaries(created_at);")

def save_summary(filename: Optional[str], source_type: str, mode: str, length: str,
                 model: str, input_chars: int, summary: str) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO summaries (created_at, filename, source_type, mode, length, model, input_chars, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            filename, source_type, mode, length, model, input_chars, summary
        ))

def search_history(query: str = "", limit: int = 50) -> List[Dict]:
    init_db()
    q = (query or "").strip().lower()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if q:
            rows = conn.execute("""
                SELECT id, created_at, filename, source_type, mode, length, model, input_chars
                FROM summaries
                WHERE LOWER(COALESCE(filename,'')) LIKE ? OR LOWER(summary) LIKE ?
                ORDER BY id DESC
                LIMIT ?;
            """, (f"%{q}%", f"%{q}%", limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT id, created_at, filename, source_type, mode, length, model, input_chars
                FROM summaries
                ORDER BY id DESC
                LIMIT ?;
            """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_summary(summary_id: int) -> Optional[Dict]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM summaries WHERE id = ?;", (summary_id,)).fetchone()
    return dict(row) if row else None
