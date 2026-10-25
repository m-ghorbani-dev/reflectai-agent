"""Inspect SQLite table schemas without permitting writes."""
import sqlite3
from pathlib import Path

def inspect_schema(db_path: str | Path) -> dict[str, list[dict[str, object]]]:
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        schema = {}
        for (table,) in tables:
            # Table names are taken from SQLite metadata and quoted safely.
            quoted = '"' + table.replace('"', '""') + '"'
            columns = connection.execute(f"PRAGMA table_info({quoted})").fetchall()
            schema[table] = [
                {"name": row[1], "type": row[2], "not_null": bool(row[3]), "default": row[4], "primary_key": bool(row[5])}
                for row in columns
            ]
        return schema
    finally:
        connection.close()
