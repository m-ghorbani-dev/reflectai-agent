"""Save each completed final answer as a standalone Markdown file."""
from datetime import datetime, timezone
from pathlib import Path
import re
from reflectai.config import ROOT_DIR

ANSWERS_DIR = ROOT_DIR / "data" / "answers"

def _slug(value: str, limit: int = 48) -> str:
    value = re.sub(r"[^\w\- ]+", "", value, flags=re.UNICODE).strip().lower()
    value = re.sub(r"[\s\-]+", "-", value)
    return (value[:limit].strip("-") or "answer")

def save_answer(prompt: str, answer: str, metadata: dict | None = None) -> Path:
    """Atomically save prompt, final answer and run metadata as Markdown."""
    ANSWERS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    stamp = now.astimezone().strftime("%Y%m%d-%H%M%S")
    path = ANSWERS_DIR / f"{stamp}_{_slug(prompt)}.md"
    details = metadata or {}
    lines = [
        "# ReflectAI — پاسخ نهایی", "",
        f"- زمان: {now.astimezone().isoformat(timespec='seconds')}",
        f"- مدل تولید: {details.get('generation_model', 'نامشخص')}",
        f"- مدل بازبینی: {details.get('reflection_model', 'نامشخص')}",
        f"- دورهای بازبینی: {details.get('rounds', 'نامشخص')}",
        f"- مدت اجرا: {details.get('duration_seconds', 'نامشخص')} ثانیه",
        "", "## درخواست", "", prompt, "", "## پاسخ نهایی", "", answer, ""
    ]
    temp = path.with_suffix(".tmp")
    temp.write_text("\n".join(lines), encoding="utf-8")
    temp.replace(path)
    return path
