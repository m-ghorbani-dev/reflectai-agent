"""Run a read-only query against an existing SQLite database."""
import sys
from reflectai.tools.schema_inspector import inspect_schema
from reflectai.tools.sql_executor import execute_read_only

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python examples/sql_example.py /path/to/database.db")
    database = sys.argv[1]
    print("Schema:")
    print(inspect_schema(database))
    columns, rows = execute_read_only(database, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print(columns)
    for row in rows:
        print(row)
