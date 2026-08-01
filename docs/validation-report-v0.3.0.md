# v0.3.0 Validation Report

## Scope

Validation covers API health/capabilities, session lifecycle, baseline query execution, deterministic follow-ups, trace retrieval, typed response validation, evidence/verification projections, Query Lab operations, structured profile comparison, and the React client build. The Retrieval Core is exercised through the existing compatibility suite; no planner, routing, retriever, processor, ranking, or evaluation semantics were changed.

## Trace-to-UI coverage

| Layer | Contract | Validation |
|---|---|---|
| A | Native `RetrievalTrace` | Existing observability tests plus raw trace download |
| B | Workbench stage/evidence projection | API tests assert stage status, details, evidence, and score stack |
| C | Pydantic DTOs | `WorkbenchResponse`, `StageSummary`, `EvidenceItem`, and verification models validate API responses |
| D | HTTP query and trace endpoints | FastAPI `TestClient` covers query, trace, sessions, errors, and Query Lab |
| E | Trace API | Trace URL resolves to the native structured trace |
| F | React state/UI | Workbench tests cover navigation, audit/evidence/trace controls, unavailable state, and structured Query Lab comparison |

## Field completeness

Planner projections include requested/actual provider and model, strategy, selected retrievers/processors, reason codes, constraints, K values, fallback state, latency, and plan fingerprint. Retriever projections include provider, input/output counts, candidate records, scores, matched fields/terms, constraint coverage, and latency. Fusion and reranking expose candidate pools, RRF contributions, provider/model identity, rank transitions, and model-load/inference timings. A graph stage that was not selected is explicitly marked `not_selected` with a reason.

Each final result has one `EvidenceItem` and one `evidence_by_result` bundle. Selecting a result updates the Evidence panel without duplicating the result biography. Verification exposes ten named findings with expected/actual values and result/evidence references. Unlabelled runs explicitly report `quality_status=unlabelled` and `quality_metrics=not_applicable`.

## Query Lab

Query Lab supports labelled case selection, repeated execution (bounded to five runs), run history, and structured comparison of planner/reranker identity, strategy, retriever set, fallback, latency, result overlap/Jaccard, rank movement, and metric deltas. Provider-specific raw scores are intentionally not compared across profiles; raw comparison JSON remains available as a secondary detail view.

## Automated results

- Python suite: **39 passed** (`python3 -m unittest discover -s tests -v`)
- Frontend tests: **4 passed** (`npm test` in `apps/workbench`)
- Frontend production build: **passed** (`npm run build`)
- Playwright browser acceptance: **4 passed** (`PLAYWRIGHT_BROWSERS_PATH=/tmp/armie-playwright npx playwright test`) using Chromium, frontend `http://127.0.0.1:5177`, backend `http://127.0.0.1:8782`
- Package build: **passed** (`python3 -m build`)
- Patch validation: **passed** (`git diff --check`)

## Manual local smoke test

The initial real-payload diagnosis reproduced stale HTTP responses on the default ports: a globally installed package was being imported before the repository source, so HTTP 200 responses contained the old projection. The launcher now always prepends the repository `src` path. Fresh baseline and model-enhanced responses contain non-empty stage details, five evidence bundles, ten verification findings, execution context, and stage/candidate metrics. Playwright then exercised the real local UI and passed Audit, Evidence selection, Verification, and model-enhanced Summary/Metrics checks.

## Limitations

Sessions are process-local, the benchmark is synthetic, and model-enhanced execution still depends on local Ollama/BGE prerequisites. Authentication, hosted persistence, streaming, and external package publication remain out of scope.
