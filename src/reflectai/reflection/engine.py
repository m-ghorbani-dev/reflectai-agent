"""Simple generate-review-revise reflection loop."""
from dataclasses import dataclass
from ..providers.registry import generate

@dataclass
class ReflectionResult:
    answer: str
    rounds: int
    review: str

def run_reflection(
    prompt: str,
    generation_provider: str,
    generation_model: str,
    reflection_provider: str,
    reflection_model: str,
    max_rounds: int = 2,
) -> ReflectionResult:
    answer = generate(
        generation_provider, generation_model, prompt,
        "Answer the user's request accurately and clearly."
    )
    review = "Reflection not run."
    for round_number in range(max(0, min(max_rounds, 5))):
        review = generate(
            reflection_provider,
            reflection_model,
            f"Review the draft against the original request. Identify factual gaps, ambiguity, and concrete improvements. If it is already good, say APPROVED.\n\nREQUEST:\n{prompt}\n\nDRAFT:\n{answer}",
            "You are a rigorous but constructive reviewer. Do not invent facts."
        )
        if "APPROVED" in review.upper():
            return ReflectionResult(answer, round_number + 1, review)
        answer = generate(
            generation_provider, generation_model,
            f"Improve the draft using this review. Return only the revised answer.\n\nREQUEST:\n{prompt}\n\nDRAFT:\n{answer}\n\nREVIEW:\n{review}",
            "Revise the answer carefully. Preserve correct details and address the review."
        )
    return ReflectionResult(answer, max(0, min(max_rounds, 5)), review)
