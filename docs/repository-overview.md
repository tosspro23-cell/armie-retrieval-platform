# Repository Overview

```text
.
├── configs/       Example runtime configuration
├── docs/          Architecture, milestone, release, and compliance records
├── examples/      Runnable Expert Discovery demonstration
├── src/           Installable `armie_retrieval` package
│   └── armie_retrieval/
│       ├── evaluation/  Observational metrics
│       ├── learning/    Offline observation and policy lifecycle
│       ├── models/      Frozen domain contracts
│       ├── planners/    Rule and LLM-compatible planners
│       ├── processors/  Ordered result processors
│       ├── providers/   In-memory and NetworkX providers
│       ├── registries/  Capability discovery and resolution
│       └── retrievers/  Dense, sparse, hybrid, and graph strategies
└── tests/         Standard-library automated tests
```

Start with [README.md](../README.md), then the [Architecture Freeze](architecture-freeze-v1.md). The milestone and release records explain the evolution without redefining architecture.
