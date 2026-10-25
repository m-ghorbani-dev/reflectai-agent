from unittest.mock import patch
import pytest
from reflectai.exceptions import ConfigurationError
from reflectai.providers.registry import available_providers, make_provider

def test_available_providers_uses_enabled_flag():
    with patch("reflectai.providers.registry.provider_settings", return_value={"providers": {"one": {"enabled": True}, "two": {"enabled": False}}}):
        assert available_providers() == ["one"]

def test_unknown_provider_fails_clearly():
    with patch("reflectai.providers.registry.provider_settings", return_value={"providers": {}}):
        with pytest.raises(ConfigurationError):
            make_provider("unknown")

def test_openai_requires_api_key():
    config = {"providers": {"openai": {"enabled": True, "base_url": "https://api.openai.com/v1"}}}
    with patch("reflectai.providers.registry.provider_settings", return_value=config), patch("reflectai.providers.registry.env_value", return_value=None):
        with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
            make_provider("openai")
