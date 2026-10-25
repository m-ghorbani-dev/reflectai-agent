# Architecture

ReflectAI is organized as a small Python package under `src/reflectai`.

- **UI**: Streamlit pages collect user inputs and display generated output, history, and SQLite results.
- **Provider registry**: creates a provider on demand, validates configuration, and records non-content usage counters.
- **Providers**: adapters translate the common `generate(prompt, model, system)` interface to Ollama or an OpenAI-compatible chat completion endpoint.
- **Reflection**: generates a first draft, requests a review, and revises only when the reviewer has not explicitly approved the draft. Review rounds are capped at five.
- **Storage**: stores a bounded JSON history locally with atomic replacement.
- **SQLite tools**: schema inspection uses a read-only connection; query execution combines a conservative validator, SQLite read-only mode, an authorizer, a progress-handler deadline, and a row cap.
- **Chart tools**: use Plotly Express to create charts from tabular query results.

The provider and UI layers are deliberately separated so providers and interfaces can be extended independently.
