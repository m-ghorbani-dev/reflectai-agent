"""Ollama provider integration with bounded context and cancellable streaming."""
from threading import Event
from ollama import Client
from .base import BaseProvider
from ..exceptions import GenerationCancelled


class OllamaProvider(BaseProvider):
    def __init__(self, host: str = "http://localhost:11434"):
        self.client = Client(host=host, timeout=600)

    def list_models(self) -> list[str]:
        response = self.client.list()
        models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        names = []
        for item in models:
            name = item.get("name") if isinstance(item, dict) else getattr(item, "model", None)
            if name and name not in names:
                names.append(name)
        return names

    def loaded_models(self) -> list[str]:
        response = self.client.ps()
        models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        result = []
        for item in models:
            name = item.get("name") or item.get("model") if isinstance(item, dict) else (getattr(item, "name", None) or getattr(item, "model", None))
            if name and name not in result:
                result.append(name)
        return result

    def unload_model(self, model: str) -> None:
        """Ask Ollama to release a model from memory."""
        self.client.generate(model=model, prompt="", keep_alive=0, stream=False)

    def unload_all(self) -> list[str]:
        models = self.loaded_models()
        for model in models:
            try:
                self.unload_model(model)
            except Exception:
                # Keep trying to unload other models if one model fails.
                continue
        return models

    def generate(self, prompt: str, model: str, system: str | None = None,
                 context_len: int = 4096, max_tokens: int = 1024,
                 cancel_event: Event | None = None, unload_after: bool = False) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        options = {"num_ctx": max(512, int(context_len)), "num_predict": max(32, int(max_tokens))}
        response = self.client.chat(
            model=model, messages=messages, options=options,
            stream=True, keep_alive=0 if unload_after else "5m",
        )
        parts = []
        try:
            for chunk in response:
                if cancel_event is not None and cancel_event.is_set():
                    close = getattr(response, "close", None)
                    if close:
                        close()
                    raise GenerationCancelled("Generation cancelled by user")
                message = chunk.get("message", {}) if isinstance(chunk, dict) else getattr(chunk, "message", {})
                content = message.get("content", "") if isinstance(message, dict) else getattr(message, "content", "")
                if content:
                    parts.append(content)
        finally:
            close = getattr(response, "close", None)
            if close:
                close()
        if cancel_event is not None and cancel_event.is_set():
            raise GenerationCancelled("Generation cancelled by user")
        return "".join(parts)
