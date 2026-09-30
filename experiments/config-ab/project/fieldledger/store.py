"""SQLite owns revision order and the current-record projection."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator

from .model import Record


SCHEMA = """
CREATE TABLE IF NOT EXISTS revisions (
    revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    day TEXT NOT NULL,
    category TEXT NOT NULL,
    value INTEGER NOT NULL,
    note TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS revisions_identity
ON revisions(source, external_id, revision_id);
"""


@contextmanager
def connect(path: str | Path) -> Iterator[sqlite3.Connection]:
    """Commit all appended revisions together, or roll back on failure."""
    connection = sqlite3.connect(path)
    try:
        connection.executescript(SCHEMA)
        with connection:
            yield connection
    finally:
        connection.close()


def current_records(connection: sqlite3.Connection) -> list[Record]:
    rows = connection.execute("""
        SELECT r.source, r.external_id, r.day, r.category, r.value, r.note
        FROM revisions AS r
        JOIN (
            SELECT source, external_id, MAX(revision_id) AS revision_id
            FROM revisions
            GROUP BY source, external_id
        ) AS latest ON r.revision_id = latest.revision_id
        ORDER BY r.source, r.external_id
    """)
    return [Record(*row) for row in rows]


def history_records(connection: sqlite3.Connection) -> list[Record]:
    rows = connection.execute("""
        SELECT source, external_id, day, category, value, note
        FROM revisions ORDER BY revision_id
    """)
    return [Record(*row) for row in rows]


def append_revision(connection: sqlite3.Connection, record: Record) -> None:
    connection.execute("""
        INSERT INTO revisions(source, external_id, day, category, value, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (record.source, record.external_id, record.day, record.category,
          record.value, record.note))


def read_current(path: str | Path) -> list[Record]:
    """Read without creating a database or initializing its schema."""
    database = Path(path)
    if not database.exists():
        return []
    connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return current_records(connection)
    finally:
        connection.close()
