#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
OLLAMA_PID=""

ollama_is_up() {
  curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1
}

cleanup() {
  echo
  echo "[ReflectAI] Stopping Streamlit and releasing Ollama model memory..."
  if command -v ollama >/dev/null 2>&1 && ollama_is_up; then
    while IFS= read -r model; do
      [[ -z "$model" ]] && continue
      echo "[ReflectAI] Unloading: $model"
      ollama stop "$model" >/dev/null 2>&1 || true
    done < <(ollama ps 2>/dev/null | awk 'NR > 1 {print $1}')
  fi
  if [[ -n "$OLLAMA_PID" ]] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
    kill "$OLLAMA_PID" 2>/dev/null || true
    wait "$OLLAMA_PID" 2>/dev/null || true
  fi
  echo "[ReflectAI] Cleanup complete."
}
trap cleanup EXIT INT TERM

if [[ -z "${CONDA_PREFIX:-}" ]]; then
  echo "Tip: activate your Conda environment first, for example: conda activate tf"
fi

if command -v ollama >/dev/null 2>&1 && ! ollama_is_up; then
  echo "[ReflectAI] Ollama is not running; starting a local server..."
  ollama serve >/tmp/reflectai-ollama.log 2>&1 &
  OLLAMA_PID=$!
  for _ in $(seq 1 30); do
    ollama_is_up && break
    sleep 1
  done
  if ! ollama_is_up; then
    echo "Ollama did not start. See /tmp/reflectai-ollama.log" >&2
    exit 1
  fi
fi

streamlit run streamlit_app.py
