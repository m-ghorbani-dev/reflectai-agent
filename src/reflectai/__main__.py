"""Allow running ReflectAI with ``python -m reflectai``."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
