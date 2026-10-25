"""Revise drafts using explicit review feedback."""
from ..providers.registry import generate

def revise_draft(prompt: str, draft: str, feedback: str, provider: str, model: str, trace: list | None = None, progress_callback=None) -> str:
    system = "Revise carefully. Do not claim to have performed actions you did not perform."
    revision_prompt = (
        "Improve the draft using the review. Preserve correct details, satisfy the original request, and return only the revised answer.\\n\\n"
        f"REQUEST:\\n{prompt}\\n\\nDRAFT:\\n{draft}\\n\\nREVIEW:\\n{feedback}"
    )
    if progress_callback:
        progress_callback({"event": "start", "stage": "revision", "provider": provider, "model": model, "prompt": revision_prompt, "system_prompt": system})
    revised = generate(provider, model, revision_prompt, system).strip()
    if trace is not None:
        trace.append({"stage": "revision", "provider": provider, "model": model,
                      "system_prompt": system, "prompt": revision_prompt, "response": revised})
    if progress_callback:
        progress_callback({"event": "complete", "stage": "revision", "provider": provider, "model": model, "prompt": revision_prompt, "system_prompt": system, "response": revised})
    return revised or draft
