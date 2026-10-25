"""Shared contracts for agent implementations."""
from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """Minimal agent contract for future tool-enabled agents."""
    @abstractmethod
    def run(self, task: str, **kwargs: Any) -> Any:
        """Execute a task and return the result."""
