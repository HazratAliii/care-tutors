"""SQLite helpers for the library database."""
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "library.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    title          TEXT    NOT NULL,
    author         TEXT    NOT NULL,
    category       TEXT    NOT NULL DEFAULT '',
    published_year INTEGER NOT NULL,
    is_borrowed    INTEGER NOT NULL DEFAULT 0,
    borrower_name  TEXT,
    created_at     TEXT    NOT NULL
);
"""


def get_db_path():
    """Database file location; override with LIBRARY_DB (used by the tests)."""
    return os.environ.get("LIBRARY_DB", str(DEFAULT_DB_PATH))


def connect():
    """Open a connection whose rows behave like dictionaries."""
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the books table if it does not exist yet."""
    with connect() as connection:
        connection.executescript(SCHEMA)
