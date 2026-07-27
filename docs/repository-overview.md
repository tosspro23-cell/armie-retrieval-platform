# Repository Overview

```text
.
├── configs/       Demonstration, production, and explicit runtime profiles
├── docs/          Architecture, milestone, release, compliance, and validation records
├── examples/      Expert Discovery, benchmark, and production-validation commands
├── src/           Installable `armie_retrieval` package
│   └── armie_retrieval/
│       ├── evaluation/  Observational metrics
│       ├── benchmarking/ Deterministic, index-independent benchmark sources
│       ├── embeddings/  Replaceable local production embedding providers
│       ├── indexing/    Offline vector, keyword, and graph index builders
│       ├── learning/    Offline observation and policy lifecycle
│       ├── models/      Frozen domain contracts
│       ├── observability/ Optional trace models, collection, rendering, and JSON export
│       ├── planners/    Rule and LLM-compatible planners
│       ├── processors/  Ordered result processors
│       ├── providers/   In-memory and NetworkX providers
│       ├── rerankers/   Explicit no-op, metadata, and local cross-encoder providers
│       ├── registries/  Capability discovery and resolution
│       ├── retrievers/  Demonstration and persistent-index retrieval strategies
│       └── vectorstores/ Persistent FAISS vector-store adapter
└── tests/         Standard-library automated tests
```

Start with [README.md](../README.md), then the [Architecture Freeze](architecture-freeze-v1.md). The [v0.2.3 Release Notes](release-notes-v0.2.3.md) and [Validation Report](validation-report-v0.2.3.md) describe model-enhanced retrieval; the [v0.2.2 Release Notes](release-notes-v0.2.2.md) describe observability.
