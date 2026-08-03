#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
UI_HOST="${UI_HOST:-localhost}"
UI_PORT="${UI_PORT:-5173}"
BACKEND_PID=""
FRONTEND_PID=""
BACKEND_LOG="$(mktemp -t armie-workbench-backend.XXXXXX.log)"

cleanup() {
  trap - EXIT INT TERM
  for pid in "$FRONTEND_PID" "$BACKEND_PID"; do
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  rm -f "$BACKEND_LOG"
}
trap cleanup EXIT INT TERM

cd "$ROOT"
echo "ARMIE Retrieval Workbench v0.4.0"
echo "Repository: $ROOT"
echo "Python: $PYTHON_BIN ($($PYTHON_BIN -c 'import sys; print(sys.executable)' 2>/dev/null || echo unavailable))"

# Always prefer the repository source tree. A globally installed ARMIE package
# may be older than the checkout and would otherwise make the HTTP process serve
# stale Workbench projections while the frontend appears healthy.
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

if ! "$PYTHON_BIN" -c 'import fastapi, uvicorn' 2>/dev/null; then
  echo "ERROR: FastAPI and uvicorn are required." >&2
  echo "Install them with: $PYTHON_BIN -m pip install -e ." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import armie_retrieval' 2>/dev/null; then
  echo "ERROR: armie_retrieval is not importable from the repository source tree." >&2
  echo "Preferred setup: $PYTHON_BIN -m pip install -e $ROOT" >&2
  echo "Repository-local fallback: PYTHONPATH=$ROOT/src $PYTHON_BIN -m uvicorn services.api.app:app" >&2
  exit 1
fi
echo "Using repository-local source: PYTHONPATH=$ROOT/src"

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is required for the Workbench frontend." >&2
  echo "Install Node.js/npm, then run: (cd apps/workbench && npm install)" >&2
  exit 1
fi
if [ ! -f "$ROOT/apps/workbench/node_modules/vite/bin/vite.js" ]; then
  echo "ERROR: frontend dependencies are not installed." >&2
  echo "Run: cd $ROOT/apps/workbench && npm install" >&2
  exit 1
fi

check_port() {
  "$PYTHON_BIN" - "$1" <<'PY'
import socket, sys
port = int(sys.argv[1])
sock = socket.socket()
try:
    sock.bind(("127.0.0.1", port))
except OSError:
    raise SystemExit(1)
finally:
    sock.close()
PY
}
if ! check_port "$API_PORT"; then echo "ERROR: API port $API_PORT is unavailable." >&2; exit 1; fi
if ! check_port "$UI_PORT"; then echo "ERROR: frontend port $UI_PORT is unavailable." >&2; exit 1; fi

"$PYTHON_BIN" -m uvicorn services.api.app:app --host "$API_HOST" --port "$API_PORT" >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
health_url="http://$API_HOST:$API_PORT/api/v1/health"
ready=0
for _ in $(seq 1 60); do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "ERROR: backend exited before becoming healthy." >&2
    cat "$BACKEND_LOG" >&2
    exit 1
  fi
  if "$PYTHON_BIN" - "$health_url" <<'PY'
import sys, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1], timeout=1) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
  then ready=1; break; fi
  sleep 0.25
done
if [ "$ready" -ne 1 ]; then
  echo "ERROR: backend did not become healthy at $health_url" >&2
  cat "$BACKEND_LOG" >&2
  exit 1
fi

(cd "$ROOT/apps/workbench" && npm run dev -- --host "$UI_HOST" --port "$UI_PORT") &
FRONTEND_PID=$!
echo "Backend: http://$API_HOST:$API_PORT"
echo "Swagger: http://$API_HOST:$API_PORT/docs"
echo "Frontend: http://$UI_HOST:$UI_PORT"
echo "Press Ctrl+C to stop both processes."

while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do sleep 1; done
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then echo "ERROR: backend stopped unexpectedly." >&2; else echo "ERROR: frontend stopped unexpectedly." >&2; fi
exit 1
