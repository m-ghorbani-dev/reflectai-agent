"""OpenAI-compatible provider integration with bounded output and cancellation."""
from threading import Event
from openai import OpenAI
from .base import BaseProvider
from ..exceptions import GenerationCancelled


class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=600)

    def generate(self, prompt: str, model: str, system: str | None = None,
                 context_len: int = 4096, max_tokens: int = 1024,
                 cancel_event: Event | None = None, unload_after: bool = False) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        stream = self.client.chat.completions.create(
            model=model, messages=messages, max_tokens=max(32, int(max_tokens)), stream=True,
        )
        parts = []
        try:
            for chunk in stream:
                if cancel_event is not None and cancel_event.is_set():
                    close = getattr(stream, "close", None)
                    if close:
                        close()
                    raise GenerationCancelled("Generation cancelled by user")
                if chunk.choices and chunk.choices[0].delta.content:
                    parts.append(chunk.choices[0].delta.content)
        finally:
            close = getattr(stream, "close", None)
            if close:
                close()
        if cancel_event is not None and cancel_event.is_set():
            raise GenerationCancelled("Generation cancelled by user")
        return "".join(parts)
