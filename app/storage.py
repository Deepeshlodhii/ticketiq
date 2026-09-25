import sqlite3
from pathlib import Path

from app.config import DATABASE_PATH


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            transaction_id TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            tier TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stages (
            transaction_id TEXT,
            stage_name TEXT,
            status TEXT,
            output TEXT,
            error TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (transaction_id, stage_name)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            feedback INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ticket_runs (
            transaction_id TEXT PRIMARY KEY,
            bandit_state TEXT NOT NULL,
            bandit_action TEXT NOT NULL,
            latency_seconds REAL NOT NULL,
            feedback INTEGER,
            reward REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()
