"""Basic read-only SQL guard. This is a guardrail, not a full SQL parser."""
import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|"
    r"reindex|truncate|grant|revoke|execute|call)\b",
    re.IGNORECASE,
)

def validate_read_only_sql(query: str) -> str:
    sql = query.strip()
    if not sql:
        raise ValueError("SQL query cannot be empty.")
    if ";" in sql.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")
    if not re.match(r"^(select|with)\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT or WITH queries are allowed.")
    if FORBIDDEN.search(sql):
        raise ValueError("Query contains a forbidden SQL operation.")
    return sql.rstrip(";")
