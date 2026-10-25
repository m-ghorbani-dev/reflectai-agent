"""Evaluate a draft using a configured language model."""
from .schemas import Review
from ..providers.registry import generate

_APPROVAL_MARKERS = ("APPROVED", "NO CHANGES NEEDED", "READY AS IS")

def evaluate_draft(prompt: str, draft: str, provider: str, model: str, trace: list | None = None, progress_callback=None) -> Review:
    system = "You are a rigorous, constructive reviewer. Evaluate the draft, not the user."
    review_prompt = (
        "Review the draft against the request. Identify correctness issues, missing requirements, ambiguity, and concrete improvements. "
        "If no material improvement is needed, begin your response with exactly 'APPROVED:'. Do not invent facts.\\n\\n"
        f"REQUEST:\\n{prompt}\\n\\nDRAFT:\\n{draft}"
    )
    if progress_callback:
        progress_callback({"event": "start", "stage": "reflection", "round": 0, "provider": provider, "model": model, "prompt": review_prompt, "system_prompt": system})
    text = generate(provider, model, review_prompt, system).strip()
    if trace is not None:
        trace.append({"stage": "reflection", "provider": provider, "model": model,
                      "system_prompt": system, "prompt": review_prompt, "response": text})
    if progress_callback:
        progress_callback({"event": "complete", "stage": "reflection", "provider": provider, "model": model, "prompt": review_prompt, "system_prompt": system, "response": text})
    first_line = text.splitlines()[0].upper() if text else ""
    approved = any(first_line.startswith(marker) for marker in _APPROVAL_MARKERS)
    return Review(approved=approved, feedback=text or "The reviewer returned an empty response.")
