#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"

FRONTEND_PORT="${FRONTEND_PORT:-3000}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found in PATH."
  exit 1
fi

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "python/python3 is required but was not found in PATH."
  exit 1
fi

if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  echo "frontend/package.json not found."
  exit 1
fi

if command -v ss >/dev/null 2>&1; then
  if ss -ltn | awk '{print $4}' | grep -qE "[:.]${FRONTEND_PORT}$"; then
    echo "Frontend port ${FRONTEND_PORT} is already in use. Set FRONTEND_PORT to another value."
    exit 1
  fi

  if ss -ltn | awk '{print $4}' | grep -qE "[:.]${BACKEND_PORT}$"; then
    echo "Backend port ${BACKEND_PORT} is already in use. Set BACKEND_PORT to another value."
    exit 1
  fi
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "Creating backend virtual environment at .venv..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"

if ! "$VENV_PY" -c "import fastapi, uvicorn, dotenv" >/dev/null 2>&1; then
  echo "Installing backend dependencies into .venv..."
  "$VENV_PY" -m pip install --upgrade pip
  "$VENV_PY" -m pip install -r "$ROOT_DIR/backend/data/requirements.txt"
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  (cd "$FRONTEND_DIR" && npm ci)
fi

cleanup() {
  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:${BACKEND_PORT}"
(
  cd "$ROOT_DIR"
  "$VENV_PY" -m uvicorn backend.main:app --reload --reload-dir backend --reload-exclude "frontend/*" --reload-exclude ".venv/*" --reload-exclude "node_modules/*" --host 0.0.0.0 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:${FRONTEND_PORT}"
(
  cd "$FRONTEND_DIR"
  env UV_THREADPOOL_SIZE=4 npm run dev -- --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

wait -n "$BACKEND_PID" "$FRONTEND_PID"

echo "One service exited. Shutting down the other..."
cleanup
