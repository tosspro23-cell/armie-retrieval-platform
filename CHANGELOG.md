# Changelog

All notable changes to this project are documented in this file.

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
