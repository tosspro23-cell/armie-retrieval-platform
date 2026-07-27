# Release Notes — v0.2.2

ARMIE Retrieval Platform v0.2.2 is a Retrieval Observability release. It adds structured, optional trace collection around the existing runtime while retaining the Architecture Freeze v1.0 responsibilities and retrieval semantics.

## Included

- `RetrievalTrace` schema: planner, retriever candidates, fusion, ranking, ground truth, evaluation, timing, and warnings.
- Per-candidate dense/keyword field evidence, NetworkX graph-edge evidence, RRF contribution records, and processor-aware final ranking.
- Shared evaluation calculation explanations for Precision@K, Recall@K, MRR, NDCG@K, and latency.
- Terminal renderer, JSON export, benchmark CLI, and retrieval ablation modes.

## Compatibility

`RetrievalRuntime.execute` remains unchanged. `execute_with_trace` is an optional extension. The same planner and configuration return the same retrieval results with or without trace collection.

## Boundaries

The trace reports observable structured outputs and evidence only. It does not emit hidden model reasoning, invent semantic explanations, alter provider interfaces, or change retrieval/fusion/ranking algorithms.
