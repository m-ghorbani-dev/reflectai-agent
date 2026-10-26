"""Provider construction and model invocation with lazy optional imports."""
from ..config import provider_settings, env_value
from ..exceptions import ConfigurationError, ProviderError
from ..observability.usage import record_usage
from ..observability.logging import get_logger

logger = get_logger(__name__)

def available_providers() -> list[str]:
    cfg = provider_settings().get("providers", {})
    return [name for name, item in cfg.items() if isinstance(item, dict) and item.get("enabled", False)]

def make_provider(name: str):
    cfg = provider_settings().get("providers", {}).get(name, {})
    if not isinstance(cfg, dict) or not cfg.get("enabled", False):
        raise ConfigurationError(f"Provider '{name}' is not enabled in config/providers.yaml")
    if name == "ollama":
        try:
            from .ollama import OllamaProvider
        except ImportError as exc:
            raise ProviderError("Ollama Python package is missing. Install project requirements.") from exc
        return OllamaProvider(host=cfg.get("base_url", "http://localhost:11434"))
    if name == "openai":
        api_key = env_value("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError("OPENAI_API_KEY is not set. Add it to .env to use the OpenAI provider.")
        try:
            from .openai_compatible import OpenAICompatibleProvider
        except ImportError as exc:
            raise ProviderError("OpenAI Python package is missing. Install project requirements.") from exc
        return OpenAICompatibleProvider(api_key=api_key, base_url=env_value("OPENAI_BASE_URL", cfg.get("base_url")))
    raise ConfigurationError(f"Unknown provider: {name}")

def list_models(provider: str) -> list[str]:
    """List available models for providers that support model discovery."""
    if provider == "ollama":
        return make_provider(provider).list_models()
    return []

def generate(provider: str, model: str, prompt: str, system: str | None = None,
             context_len: int = 4096, max_tokens: int = 1024, cancel_event=None,
             unload_after: bool = False) -> str:
    if not model or not model.strip():
        raise ConfigurationError("Model name cannot be empty")
    try:
        result = make_provider(provider).generate(
            prompt=prompt, model=model.strip(), system=system, context_len=context_len,
            max_tokens=max_tokens, cancel_event=cancel_event, unload_after=unload_after,
        )
        if not isinstance(result, str) or not result.strip():
            raise ProviderError(f"Provider '{provider}' returned an empty response")
        record_usage(provider, "success")
        return result.strip()
    except Exception:
        record_usage(provider, "error")
        logger.exception("Model request failed for provider=%s model=%s", provider, model)
        raise
