# ARMIE Retrieval Platform — Validation Report v0.2.1

**Date:** 2026-07-26  
**Status:** Implemented and locally validated

## Scope and architectural boundary

This release validates production-ready implementations while retaining Architecture Freeze v1.0:

- The planner continues to emit immutable, declarative `RetrievalPlan` objects.
- The existing `RetrievalRuntime` continues to resolve a retriever, execute it, and apply ordered result processors.
- Retriever, processor, and provider registries remain separate; index artifacts are not registry entries.
- Retrievers consume offline-built indexes only.
- Evaluation observes `RetrievalResult` without mutating it.

No planner, runtime, registry, retrieval contract, provider-interface, or evaluation-workflow redesign was made.

## Local validation evidence

The following command completed successfully:

```bash
python3 examples/production_validation.py --artifacts /private/tmp/armie-validation-v021 --size 50
```

| Validation | Result |
|---|---|
| 50-expert knowledge generation | Passed |
| Persistent FAISS vector index | Passed |
| Persistent keyword index | Passed |
| Persisted NetworkX graph index and graph retrieval | Passed (3 results) |
| Dense, sparse, hybrid, and graph execution through existing runtime | Passed |
| Precision@K, Recall@K, MRR, NDCG@K, latency | Generated |
| Local Ollama planner (`qwen3:4b`) | Passed; returned `hybrid` strategy |
| BGE-M3 local model validation and embedding execution | Passed |

The fixture reported Precision@5 **0.3333**, Recall@5 **0.8333**, MRR **0.7778**, and NDCG@5 **0.7689**. The generated JSON report records the environment-specific mean latency. These figures validate the indexing and evaluation pipeline only: the fixture uses deterministic test vectors, not BGE-M3 vectors.

## BGE-M3 portability prerequisite

The local environment used for the release review contains `BAAI/bge-m3`, and the validation runner successfully generated an embedding from it. The provider remains lazy and does not download model weights automatically.

On another machine, explicitly download the model before production-embedding validation:

```bash
huggingface-cli download BAAI/bge-m3
python3 examples/production_validation.py --size 50
```

Once the model is available, the same validation runner reports `"bge_model_validation": "passed"` and its embedding dimension; no code or architecture change is required.

## Test suite

```bash
python3 -m unittest discover -s tests -v
```

The suite covers the existing v0.2 contracts plus persisted artifacts, benchmark-source separation, NDCG, and the Ollama structured-client contract. All tests passed locally.
