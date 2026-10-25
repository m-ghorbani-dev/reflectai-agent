"""Small in-memory usage counters; deliberately excludes prompts and secrets."""
from collections import Counter
from threading import Lock

_counts: Counter[str] = Counter()
_lock = Lock()

def record_usage(provider: str, outcome: str = "success") -> None:
    key = f"{provider}:{outcome}"
    with _lock:
        _counts[key] += 1

def usage_summary() -> dict[str, int]:
    with _lock:
        return dict(_counts)

def reset_usage() -> None:
    with _lock:
        _counts.clear()
