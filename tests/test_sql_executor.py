import sqlite3
import pytest
from reflectai.exceptions import SQLSafetyError
from reflectai.tools.sql_executor import execute_read_only
from reflectai.tools.schema_inspector import inspect_schema

def make_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
    conn.executemany("INSERT INTO items(name) VALUES (?)", [(f"item-{i}",) for i in range(10)])
    conn.commit(); conn.close()

def test_query_and_limit(tmp_path):
    db = tmp_path / "sample.db"; make_db(db)
    columns, rows = execute_read_only(db, "SELECT id, name FROM items ORDER BY id", limit=3)
    assert columns == ["id", "name"]
    assert len(rows) == 3

def test_query_cannot_write(tmp_path):
    db = tmp_path / "sample.db"; make_db(db)
    with pytest.raises((ValueError, sqlite3.DatabaseError)):
        execute_read_only(db, "DELETE FROM items")
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 10
    conn.close()

def test_multiple_statements_rejected(tmp_path):
    db = tmp_path / "sample.db"; make_db(db)
    with pytest.raises(ValueError):
        execute_read_only(db, "SELECT 1; SELECT 2")

def test_schema_inspector(tmp_path):
    db = tmp_path / "sample.db"; make_db(db)
    schema = inspect_schema(db)
    assert "items" in schema
    assert schema["items"][0]["name"] == "id"
