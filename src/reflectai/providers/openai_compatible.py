"""OpenAI-compatible provider integration."""
from openai import OpenAI
from .base import BaseProvider

class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, model: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content or ""
