"""SQL agent scaffold; execution is handled by the restricted SQL tool."""
from ..providers.registry import generate

def generate_sql(question: str, schema: str, provider: str, model: str) -> str:
    return generate(
        provider, model,
        f"Write one read-only SQLite SELECT query answering the question. Return SQL only. Do not use multiple statements.\n\nSCHEMA:\n{schema}\n\nQUESTION:\n{question}",
        "You generate safe, read-only SQLite queries."
    )
