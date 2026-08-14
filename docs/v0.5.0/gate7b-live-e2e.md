# Gate 7B — Live Workbench E2E

Status: bounded live-integration preparation; no commit, release, or Gate 8
work was started.

## Canonical startup

The repository-supported launcher is:

```text
make workbench
```

It runs `scripts/start_workbench.sh`, which starts:

- backend: `PYTHONPATH=src python3 -m uvicorn services.api.app:app
  --host 127.0.0.1 --port 8000`;
- frontend: `cd apps/workbench && npm run dev -- --host localhost --port
  5173`;
- API base: `http://127.0.0.1:8000/api/v1`;
- UI: `http://localhost:5173`.

For this bounded run, the same launcher was isolated to API port `8782` and UI
port `5177` because the canonical ports already had user-managed processes.
The Elasticsearch service remained the local `http://127.0.0.1:9200`; it was
not started or stopped by this task.

The configured Gate 6B dense identity is:

- Elasticsearch `8.15.3`;
- index `armie-experts-v1-v2-gate6b-dense-10000`;
- 10,000 documents;
- `BAAI/bge-m3`, 1024 dimensions;
- projection schema `armie-v0.5-constraint-projection-v1`;
- projection implementation `constraint-projection-0.2-gate6b`.

## Readiness evidence

The live backend returned HTTP 200 for `/api/v1/health`,
`/api/v1/capabilities`, and `/api/v1/constraints/registry`. The capability
response exposed the promoted C1 registry and the registry endpoint returned
the supported field/operator contract without raw backend DSL. The local
Elasticsearch integration checks passed against the running 8.15.3 cluster.

The live browser loaded the Workbench at `http://127.0.0.1:5177/`. A real free
query rendered five H2 results with `Dense score`, runtime diagnostics, and an
explicit unlabelled-quality state. This confirms browser → frontend → backend
connectivity for the existing Workbench path.

## Playwright

The repository Playwright suite completed with status `passed` and no failed
tests (`apps/workbench/test-results/.last-run.json`). It used the repository's
configured local web servers and Chromium browser. Frontend unit tests and the
production build also passed.

## Important integration boundary

The current Workbench service's H1–H4/Free Query orchestration still uses its
existing in-memory benchmark runtime. The live C1 Elasticsearch provider was
validated directly against the compatible index, but the Workbench has no
structured RetrievalContract request surface or Elasticsearch runtime wiring
in this bounded task. Therefore browser-level C1 cases (years, seniority,
exclusion, multi-constraint, strict shortfall, and unsupported contract
rejection) are **not claimed as passed**. They remain manual/product-integration
follow-up items rather than fabricated E2E evidence.

No C1 fallback to C0/C2 was observed in the direct provider proof, and no
runtime semantics were changed to conceal this Workbench boundary.
