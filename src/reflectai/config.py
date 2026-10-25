"""Configuration helpers for ReflectAI."""
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv
from .exceptions import ConfigurationError

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env", override=False)

def load_yaml(relative_path: str) -> dict:
    path = (ROOT_DIR / relative_path).resolve()
    if ROOT_DIR.resolve() not in path.parents:
        raise ConfigurationError("Configuration path must stay inside the project directory")
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Unable to read configuration file: {relative_path}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigurationError(f"Configuration file must contain a YAML mapping: {relative_path}")
    return data

def app_settings() -> dict:
    return load_yaml("config/settings.yaml")

def provider_settings() -> dict:
    return load_yaml("config/providers.yaml")

def env_value(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)
