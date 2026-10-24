"""Ollama provider integration."""
from ollama import Client
from .base import BaseProvider

class OllamaProvider(BaseProvider):
    def __init__(self, host: str = "http://localhost:11434"):
        self.client = Client(host=host)

    def generate(self, prompt: str, model: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat(model=model, messages=messages)
        return response["message"]["content"]
