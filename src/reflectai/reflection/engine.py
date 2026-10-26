"""Bounded generate-review-revise reflection workflow."""
from threading import Event
from .schemas import ReflectionResult
from .evaluator import evaluate_draft
from .reviser import revise_draft
from .stopping import normalize_rounds
from ..providers.registry import generate
from ..exceptions import GenerationCancelled


def run_reflection(prompt: str, generation_provider: str, generation_model: str,
                   reflection_provider: str, reflection_model: str, max_rounds: int = 2,
                   progress_callback=None, context_len: int = 4096, max_tokens: int = 1024,
                   cancel_event: Event | None = None, unload_after: bool = False) -> ReflectionResult:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    rounds_allowed = normalize_rounds(max_rounds)
    trace = []
    generation_system = "Answer the user's request accurately and clearly. If uncertain, say so."

    def check_cancelled():
        if cancel_event is not None and cancel_event.is_set():
            raise GenerationCancelled("Generation cancelled by user")

    check_cancelled()
    if progress_callback:
        progress_callback({"event": "start", "stage": "generation", "round": 0, "provider": generation_provider, "model": generation_model, "prompt": prompt, "system_prompt": generation_system})
    answer = generate(generation_provider, generation_model, prompt, generation_system,
                      context_len=context_len, max_tokens=max_tokens, cancel_event=cancel_event,
                      unload_after=unload_after).strip()
    check_cancelled()
    if not answer:
        raise ValueError("The generation provider returned an empty answer")
    trace.append({"stage": "generation", "round": 0, "provider": generation_provider,
                  "model": generation_model, "system_prompt": generation_system,
                  "prompt": prompt, "response": answer})
    if progress_callback:
        progress_callback({"event": "complete", "stage": "generation", "round": 0, "provider": generation_provider, "model": generation_model, "prompt": prompt, "system_prompt": generation_system, "response": answer})
    review_text = "Reflection disabled (maximum rounds is 0)." if rounds_allowed == 0 else "Review not run."
    rounds_completed = 0
    for round_number in range(rounds_allowed):
        check_cancelled()
        review = evaluate_draft(prompt, answer, reflection_provider, reflection_model, trace=trace,
                                progress_callback=lambda event, rn=round_number + 1: progress_callback({**event, "round": rn}) if progress_callback else None,
                                context_len=context_len, max_tokens=max_tokens, cancel_event=cancel_event,
                                unload_after=unload_after)
        check_cancelled()
        review_text = review.feedback
        rounds_completed = round_number + 1
        if review.approved:
            break
        trace_before_revision = len(trace)
        answer = revise_draft(prompt, answer, review.feedback, generation_provider, generation_model,
                              trace=trace,
                              progress_callback=lambda event, rn=round_number + 1: progress_callback({**event, "round": rn}) if progress_callback else None,
                              context_len=context_len, max_tokens=max_tokens, cancel_event=cancel_event,
                              unload_after=unload_after)
        check_cancelled()
        if len(trace) > trace_before_revision and trace[-1].get("stage") == "revision":
            trace[-1]["round"] = round_number + 1
    trace.append({"stage": "final", "round": rounds_completed, "response": answer})
    return ReflectionResult(answer=answer, rounds=rounds_completed, review=review_text, trace=trace)
