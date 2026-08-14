# Gate 7C — Workbench-to-C1 Integration

Status: bounded integration closure; no release, Gate 8, commit, tag, or push.

## Request flow

The Workbench now has two explicit paths:

```text
free query
  → POST /api/v1/query
  → existing H2/C0 Dense runtime

trusted structured contract
  → POST /api/v1/structured-query
  → RetrievalContract validation
  → C1 constraint_prefilter
  → Elasticsearch 8.15.3 Gate 6B dense projection
  → structured provenance and rendered results
```

The structured path accepts contract JSON from explicit controls. It does not
extract constraints from natural language. The frontend obtains the supported
field list from `/api/v1/constraints/registry`; it does not maintain a second
capability registry.

Supported v0.5 fields are `years_experience`, `industry`, `role`, `location`,
and `seniority`, plus approved exclusions and conjunctions. Temporal,
relationship, evidence, and delivery semantics remain deferred.

## Live environment

- Backend: `PYTHONPATH=src API_PORT=8782 python3 -m uvicorn services.api.app:app --host 127.0.0.1 --port 8782`
- Frontend: `VITE_PROXY_TARGET=http://127.0.0.1:8782 UI_PORT=5177 npm run dev -- --host 127.0.0.1 --port 5177`
- Elasticsearch: `http://127.0.0.1:9200`
- Index: `armie-experts-v1-v2-gate6b-dense-10000`
- Elasticsearch: `8.15.3`
- Documents: `10,000`
- Embedding: `BAAI/bge-m3`, 1024 dimensions
- Projection: `armie-v0.5-constraint-projection-v1`, Gate 6B implementation

The canonical `make workbench` launcher was used with isolated ports because
8000 and 5173 were already occupied by user-managed processes.

## Browser E2E results

The new `tests/gate7c.integration.spec.ts` suite passed 7/7 through the real
browser → frontend → backend → Elasticsearch path:

| Scenario | Result |
| --- | --- |
| No contract → C0/H2 Dense | Passed; no filter, Dense score |
| Years experience constraint | Passed; `C1`, valid contract, native filter |
| Seniority constraint | Passed as part of conjunction coverage; `C1` |
| Explicit exclusion | Passed; exclusion shown in contract summary |
| Industry + years + seniority | Passed; conjunction and trace rendered |
| Unsupported deferred constraint | Passed; explicit unsupported state, no retrieval/fallback |
| Strict shortfall | Passed; `returned 0 of 5 requested`, no backfill |
| C1 provenance | Passed; strategy, compatibility, filter, and trace visible |

The focused legacy Workbench plus Gate 7C suite passed 11/11. The complete
Workbench Playwright suite then passed 28/28 after aligning two stale
expectations with the current H2/C0 and runtime-diagnostics presentation. The
Gate 7C acceptance evidence is the 7/7 run above.

## Contract states

- `VALID`: C1 executes against the compatible Gate 6B index.
- `UNSUPPORTED_CONSTRAINT`: deferred categories are returned explicitly and
  do not issue an Elasticsearch request.
- `INVALID_CONTRACT`: malformed or contradictory contracts are returned as a
  distinct typed state and do not issue an Elasticsearch request.

No C0 fallback, C2 route, C3 behavior, natural-language extraction, or
deferred semantic support was added.

## Provenance and shortfall

C1 responses expose strategy identity, contract state, requested/returned K,
shortfall, index/projection identity, filter application, constraint trace,
and latency. The UI shows a concise contract summary and an explicit strict
shortfall message; detailed trace data remains available under Raw Trace.

## Remaining boundary

The 10K live C1 path is now browser-integrated. Founder/manual visual review
remains separate from automated acceptance and is tracked in the Gate 7B
checklist.
