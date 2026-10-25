"""Conservative pre-validation for read-only SQLite queries.

SQLite's read-only connection and authorizer in ``tools.sql_executor`` are the
actual enforcement boundary. This validator is an additional early guardrail.
"""
import re
from ..exceptions import SQLSafetyError

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|"
    r"reindex|truncate|grant|revoke|execute|call|load_extension)\b", re.IGNORECASE
)

def _strip_leading_comments(sql: str) -> str:
    # Remove leading comments so they cannot disguise a non-SELECT statement.
    previous = None
    while previous != sql:
        previous = sql
        sql = re.sub(r"^\s*--[^\n]*(?:\n|$)", "", sql)
        sql = re.sub(r"^\s*/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.lstrip()

def validate_read_only_sql(query: str) -> str:
    if not isinstance(query, str):
        raise SQLSafetyError("SQL query must be text.")
    sql = _strip_leading_comments(query).strip()
    if not sql:
        raise SQLSafetyError("SQL query cannot be empty.")
    # Permit one trailing semicolon, but reject any other statement separator.
    candidate = sql[:-1] if sql.endswith(";") else sql
    if ";" in candidate:
        raise SQLSafetyError("Only one SQL statement is allowed.")
    if not re.match(r"^(select|with)\b", sql, re.IGNORECASE):
        raise SQLSafetyError("Only SELECT or WITH queries are allowed.")
    if _FORBIDDEN.search(sql):
        raise SQLSafetyError("Query contains a forbidden SQL operation.")
    return candidate.strip()
