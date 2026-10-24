"""Common interface for text-generation providers."""
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str, system: str | None = None) -> str:
        """Generate text from a prompt."""
