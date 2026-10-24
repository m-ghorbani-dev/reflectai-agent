"""Provider construction and model invocation."""
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider
from ..config import provider_settings, env_value

def available_providers() -> list[str]:
    cfg = provider_settings().get("providers", {})
    return [name for name, item in cfg.items() if item.get("enabled", False)]

def make_provider(name: str):
    cfg = provider_settings().get("providers", {}).get(name, {})
    if name == "ollama":
        return OllamaProvider(host=cfg.get("base_url", "http://localhost:11434"))
    if name == "openai":
        return OpenAICompatibleProvider(
            api_key=env_value("OPENAI_API_KEY"),
            base_url=env_value("OPENAI_BASE_URL", cfg.get("base_url")),
        )
    raise ValueError(f"Unknown provider: {name}")

def generate(provider: str, model: str, prompt: str, system: str | None = None) -> str:
    return make_provider(provider).generate(prompt=prompt, model=model, system=system)
