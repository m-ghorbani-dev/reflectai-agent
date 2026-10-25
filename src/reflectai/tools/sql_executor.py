"""Read-only SQLite execution with an authorizer, row cap, and deadline."""
import sqlite3
import time
from pathlib import Path
from ..exceptions import QueryTimeoutError, SQLSafetyError
from ..security.sql_policy import validate_read_only_sql

_WRITE_ACTIONS = {
    getattr(sqlite3, name) for name in (
        "SQLITE_INSERT", "SQLITE_UPDATE", "SQLITE_DELETE", "SQLITE_CREATE_INDEX",
        "SQLITE_CREATE_TABLE", "SQLITE_CREATE_TEMP_INDEX", "SQLITE_CREATE_TEMP_TABLE",
        "SQLITE_CREATE_TEMP_TRIGGER", "SQLITE_CREATE_TEMP_VIEW", "SQLITE_CREATE_TRIGGER",
        "SQLITE_CREATE_VIEW", "SQLITE_DROP_INDEX", "SQLITE_DROP_TABLE", "SQLITE_DROP_TEMP_INDEX",
        "SQLITE_DROP_TEMP_TABLE", "SQLITE_DROP_TEMP_TRIGGER", "SQLITE_DROP_TEMP_VIEW",
        "SQLITE_DROP_TRIGGER", "SQLITE_DROP_VIEW", "SQLITE_ALTER_TABLE", "SQLITE_REINDEX",
        "SQLITE_ANALYZE", "SQLITE_ATTACH", "SQLITE_DETACH", "SQLITE_TRANSACTION", "SQLITE_SAVEPOINT",
    ) if hasattr(sqlite3, name)
}

def _authorizer(action, arg1, arg2, database, source):
    if action in _WRITE_ACTIONS or action == getattr(sqlite3, "SQLITE_PRAGMA", -1):
        return sqlite3.SQLITE_DENY
    if action == getattr(sqlite3, "SQLITE_FUNCTION", -2) and (arg2 or arg1 or "").lower() == "load_extension":
        return sqlite3.SQLITE_DENY
    # Only read access and SELECT-related operations are allowed.
    allowed = {
        getattr(sqlite3, "SQLITE_SELECT", -100),
        getattr(sqlite3, "SQLITE_READ", -101),
        getattr(sqlite3, "SQLITE_FUNCTION", -102),
        getattr(sqlite3, "SQLITE_RECURSIVE", -103),
    }
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

def execute_read_only(db_path: str | Path, query: str, limit: int = 500, timeout_seconds: float = 3.0):
    """Return ``(columns, rows)`` from one read-only query.

    The result contains at most ``limit`` rows (clamped to 1..5000). Queries
    exceeding the time budget are interrupted by SQLite's progress handler.
    """
    sql = validate_read_only_sql(query)
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    row_limit = max(1, min(int(limit), 5000))
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    uri = path.as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, timeout=min(float(timeout_seconds), 30.0))
    deadline = time.monotonic() + float(timeout_seconds)
    timed_out = False
    def progress():
        nonlocal timed_out
        if time.monotonic() >= deadline:
            timed_out = True
            return 1
        return 0
    try:
        connection.set_authorizer(_authorizer)
        connection.set_progress_handler(progress, 1000)
        cursor = connection.execute(sql)
        columns = [item[0] for item in (cursor.description or [])]
        rows = cursor.fetchmany(row_limit + 1)
        if timed_out:
            raise QueryTimeoutError(f"Query exceeded the {timeout_seconds:g}s time limit")
        return columns, rows[:row_limit]
    except sqlite3.DatabaseError as exc:
        if timed_out or "interrupted" in str(exc).lower():
            raise QueryTimeoutError(f"Query exceeded the {timeout_seconds:g}s time limit") from exc
        if "not authorized" in str(exc).lower():
            raise SQLSafetyError("SQLite denied an operation outside the read-only policy.") from exc
        raise
    finally:
        connection.close()
