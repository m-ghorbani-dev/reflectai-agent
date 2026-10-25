"""Reflection-loop stopping rules."""
MAX_REFLECTION_ROUNDS = 5

def normalize_rounds(rounds: int) -> int:
    try:
        value = int(rounds)
    except (TypeError, ValueError) as exc:
        raise ValueError("max_rounds must be an integer between 0 and 5") from exc
    if value < 0 or value > MAX_REFLECTION_ROUNDS:
        raise ValueError("max_rounds must be between 0 and 5")
    return value
