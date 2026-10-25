import pytest
from reflectai.security.sql_policy import validate_read_only_sql

@pytest.mark.parametrize(("query", "expected"), [("SELECT 1;", "SELECT 1"), ("-- comment\nSELECT 1", "SELECT 1"), ("WITH x AS (SELECT 1) SELECT * FROM x", "WITH x AS (SELECT 1) SELECT * FROM x")])
def test_accepts_select(query, expected):
    assert validate_read_only_sql(query) == expected

@pytest.mark.parametrize("query", [
    "", "DROP TABLE products", "DELETE FROM products", "UPDATE products SET price=0",
    "SELECT 1; SELECT 2", "PRAGMA table_info(products)", "-- comment\nDROP TABLE x",
    "WITH x AS (SELECT 1) DELETE FROM products", "SELECT load_extension('x')",
])
def test_rejects_unsafe_sql(query):
    with pytest.raises(ValueError):
        validate_read_only_sql(query)
