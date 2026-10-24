"""Restricted SQLite query execution."""
import sqlite3
from pathlib import Path
from ..security.sql_policy import validate_read_only_sql

def execute_read_only(db_path: str | Path, query: str, limit: int = 500, timeout_seconds: float = 3.0):
    sql = validate_read_only_sql(query)
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=timeout_seconds)
    try:
        connection.set_progress_handler(lambda: 1, int(timeout_seconds * 1_000_000))
        cursor = connection.execute(f"SELECT * FROM ({sql}) LIMIT {max(1, min(limit, 5000))}")
        columns = [item[0] for item in cursor.description or []]
        rows = cursor.fetchall()
        return columns, rows
    finally:
        connection.close()
