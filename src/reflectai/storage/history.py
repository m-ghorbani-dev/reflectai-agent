"""Local JSON history storage with bounded retention and atomic writes."""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from ..config import ROOT_DIR, app_settings

HISTORY_PATH = ROOT_DIR / "data" / "history.json"
_LOCK = Lock()

def _limit() -> int:
    try:
        return max(1, min(int(app_settings().get("app", {}).get("history_limit", 100)), 1000))
    except (TypeError, ValueError):
        return 100

def add_entry(prompt: str, answer: str, metadata: dict | None = None) -> None:
    if not isinstance(prompt, str) or not isinstance(answer, str):
        raise TypeError("prompt and answer must be strings")
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "answer": answer,
        "metadata": metadata if isinstance(metadata, dict) else {},
    }
    with _LOCK:
        entries = get_history()
        entries.append(entry)
        payload = json.dumps(entries[-_limit():], ensure_ascii=False, indent=2)
        fd, temp_name = tempfile.mkstemp(prefix="history-", suffix=".tmp", dir=HISTORY_PATH.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, HISTORY_PATH)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

def get_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        value = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def clear_history() -> None:
    with _LOCK:
        try:
            HISTORY_PATH.unlink()
        except FileNotFoundError:
            pass
