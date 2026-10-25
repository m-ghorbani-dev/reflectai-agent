# Configuration

## Provider configuration

Edit `config/providers.yaml` to enable providers and set endpoint URLs. Provider names currently supported by the registry are `ollama` and `openai`.

## Application settings

`config/settings.yaml` defines the default models, maximum reflection rounds, and local history retention. The UI permits 0–5 reflection rounds regardless of a larger configured value.

## Environment variables

- `OPENAI_API_KEY`: required when using the OpenAI provider.
- `OPENAI_BASE_URL`: optional endpoint override.
- `REFLECTAI_LOG_LEVEL`: optional Python logging level, default `INFO`.

Copy `.env.example` to `.env`. Do not store credentials in YAML or source code.
