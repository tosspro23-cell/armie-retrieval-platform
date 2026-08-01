# Workbench User Guide

Install the package once with `python3 -m pip install -e .` (preferred), then start with `make workbench`. If editable installation is unavailable on a managed Python environment, the launcher can use the repository-local `src` fallback. Enter a natural-language expert query, choose `baseline` for deterministic execution or `model-enhanced` when Ollama and the local reranker are available, and run retrieval.

The Workbench has three navigation surfaces:

- **Workbench**: deterministic Answer Summary, ranked Results, Metrics, and the Audit, Evidence, Verification, and Raw Trace tabs.
- **Evidence**: selecting a result updates the stage-specific bundle for that result. Dense, sparse, graph, fusion, reranking, and score-stack details are shown without repeating the result biography.
- **Query Lab**: choose a labelled synthetic case, repeat it up to five times, and compare two runs by execution context, provider/model identity, overlap, ranking movement, metrics, latency, fallback, and verification state.

Audit rows expose status, provider/model, latency, candidate counts, K values, constraints, reason codes, and stage-specific details. `not_selected` and `unlabelled` are deliberate states, not missing data. Use the Raw Trace tab or download controls when the complete native trace, declarative plan, or execution report is required.

Query Lab formats latency for readability and keeps raw numeric values in the secondary JSON view. Baseline scores represent the deterministic final/RRF path; model-enhanced scores represent the Cross-Encoder stage, with RRF retained in the expanded score stack. Provider-specific scores must not be compared directly. The workbench is local-first and single-user: sessions are in memory, the benchmark is synthetic, and streaming, authentication, file upload, and hosted persistence are not included.

If the API is unavailable, the UI keeps its shell and displays the configured backend URL, the `make workbench` recovery command, and a Retry button. The browser console records the underlying request failure without exposing a stack trace in the normal UI.
