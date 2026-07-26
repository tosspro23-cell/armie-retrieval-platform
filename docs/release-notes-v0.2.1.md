# Release Notes — v0.2.1

ARMIE Retrieval Platform v0.2.1 is a production-validation release. It retains the frozen v0.2 architecture and validates it with persistent offline indexes, configurable local model providers, scalable benchmark knowledge, and production retrieval metrics.

## Highlights

- Configurable Ollama structured planner client, validated against the locally installed `qwen3:4b` model.
- Replaceable BGE-M3 embedding provider that never downloads model weights automatically.
- Offline FAISS vector, keyword, and NetworkX graph indexing; online retrievers consume prebuilt artifacts only.
- 50, 200, and 500-expert benchmark generation, with knowledge sources separate from indexes.
- Precision@K, Recall@K, MRR, NDCG@K, and latency evaluation.

## Compatibility

Planner, runtime, registry, retrieval contracts, provider interfaces, and evaluation workflow are unchanged. Demonstration implementations remain available; production implementations are selected through configuration and composition.

## Prerequisite

The local release review passed BGE-M3 embedding execution. On a fresh machine, `BAAI/bge-m3` must still be explicitly downloaded before the same validation. See [Validation Report v0.2.1](validation-report-v0.2.1.md).
