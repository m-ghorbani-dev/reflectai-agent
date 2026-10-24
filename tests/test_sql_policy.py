import pytest
from reflectai.security.sql_policy import validate_read_only_sql

def test_accepts_select():
    assert validate_read_only_sql("SELECT 1;") == "SELECT 1"

@pytest.mark.parametrize("query", [
    "DROP TABLE products",
    "DELETE FROM products",
    "UPDATE products SET price=0",
    "SELECT 1; SELECT 2",
    "PRAGMA table_info(products)",
])
def test_rejects_unsafe_sql(query):
    with pytest.raises(ValueError):
        validate_read_only_sql(query)
