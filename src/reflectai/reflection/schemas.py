"""Typed data structures used by the reflection workflow."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Review:
    approved: bool
    feedback: str

@dataclass(frozen=True)
class ReflectionResult:
    answer: str
    rounds: int
    review: str
    trace: list[dict] = field(default_factory=list)
