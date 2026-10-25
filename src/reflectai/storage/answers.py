"""Persist final assistant answers as readable Markdown files."""
from datetime import datetime, timezone
from pathlib import Path
import re
from ..config import ROOT_DIR


def save_final_answer(prompt: str, answer: str, metadata: dict | None = None) -> Path:
    """Write one final answer to data/answers and return its path."""
    directory = ROOT_DIR / "data" / "answers"
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", " ".join(prompt.split()).strip())[:48].strip("-") or "answer"
    path = directory / f"{stamp}_{slug}.md"
    details = metadata or {}
    lines = [
        "# ReflectAI — پاسخ نهایی",
        "",
        f"- زمان ذخیره‌سازی (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- مدل تولید: {details.get('generation_model', 'نامشخص')}",
        f"- مدل بازبینی: {details.get('reflection_model', 'نامشخص')}",
        f"- دورهای بازبینی: {details.get('rounds', 'نامشخص')}",
        f"- زمان اجرا (ثانیه): {details.get('duration_seconds', 'نامشخص')}",
        "",
        "## درخواست",
        "",
        prompt.strip(),
        "",
        "## پاسخ نهایی",
        "",
        answer.strip(),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
