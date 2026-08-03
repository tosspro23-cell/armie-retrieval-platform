# Engineering Milestones

| Version | Status | Scope |
|---|---|---|
| v0.1.0 | Complete | Runnable baseline: declarative planning, in-memory providers, sparse/dense/hybrid retrieval, processors, evaluation, and Expert Discovery. |
| v0.2.0 | Release-ready | Intelligent planner interface, capability registries, NetworkX graph retrieval, offline policy-learning MVP, and public-release readiness. |
| v0.2.1 | Production validation | Configurable local Ollama planner, replaceable BGE-M3 provider, offline FAISS/keyword/graph indexes, scalable benchmark generation, and P@K/R@K/MRR/NDCG/latency validation. |
| v0.2.2 | Retrieval observability | Optional structured trace collection, terminal/JSON inspection, component ablation, ground-truth comparison, and metric arithmetic explanations without runtime redesign. |
| v0.2.3 | Model-enhanced retrieval | Explicit deterministic/model-enhanced profiles, Ollama planner selection, bounded reranker providers, graph coverage trace, and multi-K evaluation without changing the frozen runtime flow. |
| v0.3.0 | Interactive Retrieval Workbench | Typed local API, React workbench, sessions/follow-ups, deterministic evidence and verification, audit trace projections, and Query Lab without runtime redesign. |
| v0.4.0 | Expert Discovery Relevance Engineering Foundation | Typed domain model, deterministic versioned dataset, 120-query taxonomy, graded judgements, benchmark manifests, failure analysis, and optional Elasticsearch BM25/dense data-plane adapters. |

The governing architectural record remains [Architecture Freeze v1.0](architecture-freeze-v1.md). Future changes require a new ADR and a versioned Architecture Freeze; they must not silently revise v1.0.
