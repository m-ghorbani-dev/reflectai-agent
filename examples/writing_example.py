"""Run a writing task using configured providers."""
from reflectai.agents.writing_agent import write

if __name__ == "__main__":
    result = write(
        prompt="Explain why unit tests are useful in a Python project.",
        generation_provider="ollama",
        generation_model="llama3.2",
        reflection_provider="ollama",
        reflection_model="llama3.2",
        max_rounds=1,
    )
    print(result.answer)
    print(f"Review rounds: {result.rounds}")
