from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import settings

DB_FILE = Path(settings.db_file)
DB_FILE.parent.mkdir(exist_ok=True)


def init_db() -> None:
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS datasets (id TEXT PRIMARY KEY, path TEXT NOT NULL)"
        )


def add_dataset(path: str, ds_id: str | None = None) -> str:
    import uuid

    if ds_id is None:
        ds_id = str(uuid.uuid4())
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO datasets (id, path) VALUES (?, ?)", (ds_id, path))
    return ds_id


def get_dataset_path(ds_id: str) -> Path:
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT path FROM datasets WHERE id=?", (ds_id,))
        row = cur.fetchone()
    if row is None:
        raise KeyError(ds_id)
    return Path(row[0])
