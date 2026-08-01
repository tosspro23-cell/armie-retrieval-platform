# ARMIE Retrieval Platform v0.3.0 — Interactive Retrieval Workbench

This release adds a local workbench for inspecting retrieval as a system: query context, declarative planner output, retrieval results, deterministic evidence, verification, stage summaries, and the complete existing trace.

Highlights:

- Typed FastAPI `/api/v1` service and React/Vite workbench UI.
- In-memory sessions with bounded deterministic follow-up resolution.
- Baseline and model-enhanced profile selection without duplicating the runtime pipeline.
- Deterministic answer summaries and verification; no LLM-generated claims are added.
- Query Lab cases, labelled metrics, and profile comparison.
- Expandable Audit, selected-result evidence, detailed verification findings, provider-specific score semantics, raw trace/export controls, and repeatability inspection.
- Existing Architecture Freeze remains unchanged: Planner → Retriever → Result Processor → Evaluation.

Known limitations: sessions are process-local, the benchmark is synthetic, and model-enhanced execution still depends on local Ollama/BGE prerequisites. Authentication, hosted persistence, streaming, and external package publication remain out of scope.

## Release validation

The local release was validated with the real FastAPI and Vite applications. Baseline uses the deterministic `rule` Planner and `metadata_boost` reranker; model-enhanced execution uses the Ollama `qwen3:4b` Planner and BGE Cross-Encoder when prerequisites are available. The Audit Trail exposes provider/model/fallback context, stage latency and candidate flow. Evidence is trace-derived and follows canonical result selection. Verification is deterministic and expandable, and Query Lab compares profiles by overlap, rank movement, metrics, and formatted latency deltas.

Final browser acceptance: **4 passed** using **Chromium via Playwright**. Python tests, frontend tests, frontend build, package build, and `git diff --check` also passed. Scores are provider-specific and are not directly comparable across profiles; Cross-Encoder final scores retain their RRF contribution separately in the score stack.

This remains a local-first, single-user workbench with in-memory sessions, a synthetic benchmark, no streaming, no authentication, no file upload, and no hosted production deployment. The short-lived Cross-Encoder worker and FAISS/Torch process-isolation behavior remain unchanged.
