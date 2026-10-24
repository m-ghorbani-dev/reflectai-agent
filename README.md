# ReflectAI

**A Multi-Provider AI Agent with Reflection and Iterative Refinement**

ReflectAI is an extensible Python project designed to explore AI agents that improve their outputs through iterative reflection and revision. It is being developed to support local language models and online model providers through a unified interface.

## Features

- **Multi-Provider Architecture:** Designed to support local and online language models.
- **Reflection Workflow:** A framework for evaluating and refining generated outputs.
- **Writing Agent:** Intended for writing tasks with iterative revision.
- **SQL Agent:** Planned support for generating and refining SQL queries.
- **Visualization Agent:** Planned support for data visualization workflows.
- **Streamlit Interface:** A web-based interface for interacting with the project.
- **Security:** Dedicated modules for SQL policies and execution controls.

## Architecture

```text
reflectai-agent/
├── config/          # Application and provider configuration
├── docs/            # Project documentation
├── examples/        # Example workflows
├── src/reflectai/
│   ├── agents/      # Writing, SQL, and visualization agents
│   ├── providers/   # Model provider integrations
│   ├── reflection/  # Evaluation and refinement workflow
│   ├── security/    # Execution and SQL policies
│   ├── storage/     # Conversation history
│   ├── tools/       # SQL and visualization utilities
│   └── ui/          # Streamlit interface
├── tests/           # Automated tests
└── streamlit_app.py # Streamlit entry point
```

## Requirements

- Python 3.10 or newer
- pip
- An existing Python environment
- Ollama for local model usage, when configured

## Installation

Activate your Python environment, then run:

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure the environment variables required by your selected provider.

Never commit API keys, passwords, or other secrets to GitHub.

Provider and application settings are stored in the `config/` directory.

## Run the Application

```bash
streamlit run streamlit_app.py
```

## Development

Run the test suite with:

```bash
pytest
```

## Project Status

ReflectAI is under active development. The current repository establishes the project structure and initial interface. Model integration, reflection workflows, and agent capabilities are being implemented incrementally.

## License

See the `LICENSE` file.
