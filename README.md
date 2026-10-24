# ReflectAI

**A multi-provider AI agent with reflection and iterative refinement.**

ReflectAI is an experimental Python project that lets you select separate providers and models for generation and reflection. It currently includes a Streamlit interface, Ollama and OpenAI-compatible provider adapters, a bounded review-and-revision loop, local history, and a basic read-only SQL safety layer.

## Features
- Independently select generation and reflection providers/models.
- Use local models through Ollama or an OpenAI-compatible API.
- Run a bounded reflection and revision workflow.
- Store recent prompts and answers locally.
- Inspect provider settings in the UI.
- Basic SQLite read-only query helper and SQL validation.

## Setup
Activate your existing Python environment, then run:

```bash
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

Edit `.env` only if using an online provider, and set `OPENAI_API_KEY`. Never commit `.env` or real API keys.

For Ollama, ensure the Ollama service is running and pull a model, for example:

```bash
ollama pull llama3.2
```

Run the app:

```bash
streamlit run streamlit_app.py
```

Run tests:

```bash
pytest
```

## Project status
This is an early-stage project. SQL and visualization agent modules are initial utilities and are not yet fully integrated into the UI. The SQL validator is a basic guardrail, not a substitute for sandboxing or a complete SQL parser.

## Security
- Do not commit credentials or private data.
- SQL helper opens SQLite databases in read-only mode and applies a result limit.
- Do not expose the development app publicly without authentication and security review.

## License
See `LICENSE`.
