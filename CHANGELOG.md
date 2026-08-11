# Changelog

All notable changes to this project are documented in this file.

## [0.4.0] - 2026-08-11

### Added

- Dataset v2 Expert Discovery relevance benchmark with 10,000 profiles, 120 queries, and separate Gold/Silver judgement contracts.
- Real Elasticsearch BM25 and dense retrieval, BGE-M3 embeddings, FAISS comparison, ARMIE RRF fusion, and BGE cross-encoder evaluation.
- H1–H4 Relevance Experiment Workbench with structured constraints, evidence/provenance, per-query metrics, stage-aware latency, and deterministic interpretation.
- Gate 5.5B stability and hard-negative analysis plus browser-validated Workbench acceptance coverage.

### Findings and boundaries

- Dense materially outperformed BM25 on this controlled synthetic distribution; hybrid was near-tied with dense.
- Always-on BGE reranking added substantial local CPU latency with negligible aggregate gain over H3.
- Structured relationship, temporal, and prohibited constraints remain deterministic systems concerns.
- This release makes no natural expert-network, external-human-ground-truth, production-SaaS, or universal-superiority claim.

## [0.4.0] - 2026-08-03

### Added

- Typed Expert Discovery profiles with provenance, projects, employment, and deterministic search projections.
- Reproducible dataset builder and manifest/checksum validation for small, medium, and 10,000-record scales.
- 120-query taxonomy, 0–3 relevance judgement contracts, graded metrics, failure taxonomy, and experiment manifests.
- Optional pinned Elasticsearch 8.15.3 mapping/client with BM25 and dense provider adapters alongside the existing FAISS path.
- v0.4.0 engineering specifications, dataset card, benchmark protocol, architecture decisions, and validation boundaries.

### Preserved

- v0.3.0 Workbench and shared Planner → Retriever → Result Processor → Evaluation runtime.

## [0.3.0] - 2026-08-01

### Added

- Interactive Retrieval Workbench with typed FastAPI `/api/v1` endpoints.
- Session and deterministic follow-up support, evidence projections, deterministic verification, stage summaries, and Query Lab comparison.
- React/Vite local workbench UI, startup scripts, API and user documentation.
- Discoverable Query Lab navigation, expandable trace stages, selected-result evidence, detailed verification findings, provider-specific score stacks, trace/report downloads, and repeatability/comparison views.

### Preserved

- Frozen Planner → Retriever → Result Processor → Evaluation architecture and existing trace source of truth.
- Baseline and model-enhanced profiles with controlled fallbacks.

## [0.2.3] - 2026-07-27

### Added

- Explicit fixture, baseline, and model-enhanced runtime profiles.
- Configurable Rule-based/Ollama planner selection with controlled, traceable rule fallback.
- Bounded no-op, metadata boost, and local BGE Cross-Encoder reranker providers.
- Stable expert rerank document construction, distinct candidate-pool boundaries, processor-stage traces, graph coverage, and multi-K evaluation explanations.

### Changed

- Extended `RetrievalTrace` compatibly to expose requested/actual providers, fallback state, reranker scores, and rank changes without changing the frozen runtime architecture.
- Preserved v0.2.2 deterministic behavior and clarified graph retrieval as relevance-scored matching rather than strict logical AND.
- Release-blocking patch: Planner traces now include finite reason codes, constraint types, capability descriptions, and non-mutating routing diagnostics; Cross-Encoder traces now contain every scored candidate and explicit before/after Top-K state.
- Release-blocking consistency patch: trace sections now render reranking before final ranking; fusion, rerank-pool, scoring, and final Top-K stages are distinct; metadata/no-op output uses provider-neutral fields.
- BGE Cross-Encoder execution is isolated in a JSON subprocess so the parent may use FAISS on macOS without loading Torch's conflicting OpenMP runtime. No unsafe OpenMP override is used.
- Planner ablation now records a shared, fingerprinted execution context and has separate planner-only and full-pipeline modes.

## [0.2.2] - 2026-07-27

### Added

- Optional structured `RetrievalTrace` collection for planner decisions, dense/keyword/graph candidates, hybrid fusion, final ranking, ground truth, and metric arithmetic.
- Terminal trace rendering and stable JSON export under ignored `.artifacts/traces/` directories.
- End-to-end benchmark trace CLI, including dense, keyword, graph, and hybrid ablation modes.
- Retrieval observability regression and trace-schema tests.

### Changed

- Added a backward-compatible `RetrievalRuntime.execute_with_trace` extension; normal retrieval APIs and result semantics are unchanged.
- Evaluation now exposes a shared explanation path so displayed Precision@K, Recall@K, MRR, NDCG@K, and latency use the same formulas as the evaluator.

## [0.2.1] - 2026-07-26

### Added

- Configurable local Ollama `StructuredLLMClient` with explicit service and model availability validation.
- Replaceable `BGEEmbeddingProvider`, defaulting to `BAAI/bge-m3` and deliberately requiring an explicit local model download.
- Offline indexing infrastructure for persistent FAISS vector, keyword, and NetworkX graph artifacts.
- Production retrievers that consume persisted FAISS and keyword indexes without building indexes during query execution.
- Deterministic 50, 200, and 500-expert benchmark generation, independent from index artifacts.
- Evaluation runner and NDCG@K alongside Precision@K, Recall@K, MRR, and latency.
- v0.2.1 validation example and validation report.

### Changed

- Extended the existing abstractions through providers, retrievers, and planner clients without changing the frozen runtime flow, registry architecture, or retrieval contracts.

### Known limitations

- BGE-M3 weights are not downloaded automatically. Production embedding validation requires a local model cache.
- The included validation fixture uses deterministic vectors to validate the FAISS lifecycle when BGE-M3 is not installed; it does not represent BGE retrieval-quality measurements.

## [0.2.0] - 2026-07-24

### Added

- Configurable Rule and LLM-compatible planners that produce the same declarative `RetrievalPlan`.
- Independent production-style registries for retrievers, processors, and providers.
- NetworkX-backed graph retrieval for the Expert Discovery reference scenario.
- Shared retrieval runtime and first offline policy-learning loop.
- Release documentation, Architecture Compliance Report, release notes, CI workflow, MIT licence, and public-repository metadata.

### Changed

- Packaged the project with a `src/` layout and complete Python project metadata.

### Known limitations

- The bundled LLM planner demonstration uses a deterministic structured-client fixture; selecting an API provider remains an explicit integration decision.
- Graph retrieval requires the declared `networkx` dependency.
