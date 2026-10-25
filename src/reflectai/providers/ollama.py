"""Ollama provider integration."""
from ollama import Client
from .base import BaseProvider

class OllamaProvider(BaseProvider):
    def __init__(self, host: str = "http://localhost:11434"):
        self.client = Client(host=host)

    def list_models(self) -> list[str]:
        """Return locally available Ollama model names."""
        response = self.client.list()
        models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        names = []
        for item in models:
            name = item.get("name") if isinstance(item, dict) else getattr(item, "model", None)
            if name and name not in names:
                names.append(name)
        return names

    def unload_model(self, model: str) -> None:
        """Unload a model from memory without stopping the Ollama service."""
        # Ollama's API supports an empty generation request with keep_alive=0
        # to unload the selected model immediately.
        self.client.generate(model=model, prompt="", keep_alive=0)

    def running_models(self) -> list[str]:
        """Return model names currently loaded in memory, if supported."""
        response = self.client.ps()
        models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        names = []
        for item in models:
            name = item.get("name") if isinstance(item, dict) else getattr(item, "name", None)
            if name and name not in names:
                names.append(name)
        return names

    def generate(self, prompt: str, model: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat(model=model, messages=messages)
        return response["message"]["content"]
