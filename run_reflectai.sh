#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$(realpath "$0")")"

cleanup() {
  trap - EXIT INT TERM
  echo
  echo "Stopping ReflectAI and asking Ollama to unload models..."
  python - <<'PY'
try:
    from ollama import Client
    client = Client(host="http://localhost:11434")
    response = client.ps()
    models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
    for item in models:
        name = item.get("name") if isinstance(item, dict) else getattr(item, "name", None)
        if name:
            try:
                client.generate(model=name, prompt="", keep_alive=0)
                print(f"Unloaded: {name}")
            except Exception as exc:
                print(f"Could not unload {name}: {exc}")
except Exception as exc:
    print(f"Ollama cleanup skipped: {exc}")
PY
  echo "ReflectAI stopped. Ollama service itself remains running."
}
trap cleanup EXIT INT TERM
streamlit run streamlit_app.py
