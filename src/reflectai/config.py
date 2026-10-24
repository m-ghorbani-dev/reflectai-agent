"""Configuration helpers for ReflectAI."""
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

def load_yaml(relative_path: str) -> dict:
    path = ROOT_DIR / relative_path
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    return data or {}

def app_settings() -> dict:
    return load_yaml("config/settings.yaml")

def provider_settings() -> dict:
    return load_yaml("config/providers.yaml")

def env_value(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)
