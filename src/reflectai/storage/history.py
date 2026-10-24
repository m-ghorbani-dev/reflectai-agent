"""Small local JSON history store."""
import json
from datetime import datetime, timezone
from pathlib import Path
from ..config import ROOT_DIR

HISTORY_PATH = ROOT_DIR / "data" / "history.json"

def add_entry(prompt: str, answer: str, metadata: dict | None = None) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    entries = get_history()
    entries.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "answer": answer,
        "metadata": metadata or {},
    })
    HISTORY_PATH.write_text(json.dumps(entries[-100:], ensure_ascii=False, indent=2), encoding="utf-8")

def get_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
