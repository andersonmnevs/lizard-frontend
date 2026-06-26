import sqlite3
from .config import SQLITE_PATH


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{SQLITE_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn
