# Workbench API v0.3.0

Preferred development setup:

```bash
python3 -m pip install -e .
python3 -m uvicorn services.api.app:app --host 127.0.0.1 --port 8000
```

If the editable install is not available in the current Python environment, use the repository-local fallback:

```bash
PYTHONPATH=src python3 -m uvicorn services.api.app:app --host 127.0.0.1 --port 8000
```

Or run the complete local workbench with `make workbench`; it checks imports, ports, frontend dependencies, and API health before starting Vite. Open `http://127.0.0.1:8000/docs` for Swagger.

All endpoints are under `/api/v1`. Create a session with `POST /sessions`, submit `{ "query": "...", "session_id": "...", "profile": "baseline" }` to `/query`, and inspect the returned `trace_url`. Query Lab exposes `/query-lab/cases`, `/query-lab/runs`, and `/query-lab/compare`. Errors use `{ "error": { "code", "message", "details" } }`.
