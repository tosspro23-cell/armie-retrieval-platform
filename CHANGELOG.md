# Changelog

All notable changes to this project are documented in this file.

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
