"""Writing agent using the reflection engine."""
from ..reflection.engine import run_reflection

def write(prompt: str, **kwargs):
    return run_reflection(prompt=prompt, **kwargs)
