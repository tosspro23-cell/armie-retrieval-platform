# ARMIE Retrieval Platform v0.2.3 Validation Report

## Scope

This validation covers the Model-Enhanced Retrieval release against Architecture Freeze v1.0. It extends configured providers and trace contracts; it does not redesign the planner, runtime, registry, retrieval contracts, or offline learning boundary.

## Evidence

| Check | Result |
|---|---|
| Full automated suite | Passed: 32 tests |
| Deterministic baseline production validation | Passed: FAISS, keyword, NetworkX graph artifacts, RuleBasedPlanner, hybrid retrieval, metadata reranking, trace, and evaluation |
| Ollama end-to-end path | Passed locally with `qwen3:4b`: structured plan → runtime → retrieval → reranker → final results → evaluation |
| BGE-M3 embedding availability | Passed locally |
| BGE Cross-Encoder trace | Passed locally through the isolated subprocess: 20 bounded candidates scored with before/after ranks |
| Graph constraint trace | Passed: expected/matched/missing constraints and coverage included in exported JSON |
| Wheel build | Passed: `armie_retrieval_platform-0.2.3-py3-none-any.whl` |

## Model prerequisite status

The platform intentionally does not download model weights. To activate cross-encoder execution on another machine, explicitly prepare the configured model:

```bash
huggingface-cli download BAAI/bge-reranker-v2-m3
```

Until then, the `model-enhanced` profile uses its configured deterministic fallback and records requested/actual provider state and guidance in `RetrievalTrace`.

## macOS OpenMP validation

FAISS and Torch ship conflicting `libomp.dylib` runtimes on the validation host. v0.2.3 resolves this without an unsafe `KMP_DUPLICATE_LIB_OK` override: the parent process performs FAISS retrieval and launches a short-lived BGE worker over JSON IPC. The parent does not import Torch on this path; the worker imports Torch/CrossEncoder and does not import FAISS. Worker failures are captured as structured diagnostics and may use the configured metadata fallback.

## Remaining benchmark limitation

The benchmark contains three synthetic labelled queries. Its results validate runtime behavior, observability, and ablation mechanics; they are not a general retrieval-quality claim.

## Planner and reranker observability patch

`RetrievalTrace` records finite planner `reason_codes` and `constraint_types`, requested/actual providers, selected strategy-backed retrievers, capabilities, and non-mutating routing warnings. These fields explain *what* structured criteria were selected without exposing model chain-of-thought.

Cross-Encoder trace records include every bounded candidate that was scored. `pre_rerank_rank` is the rank before the model, `reranker_rank` is the rank after model sorting, `rank_change = reranker_rank - pre_rerank_rank`, and `rank_improvement` is its inverse. The trace separately records post-rerank Top-K and final processor output, including entered/exited Top-K membership.

The ablation command compares `qwen3:4b` and `qwen3:8b` with a shared dataset/index/execution fingerprint. `planner-only` deliberately reports no downstream metrics; `full-pipeline` uses the same profile-selected reranker as the main trace. A model default may change only after repeatable routing-quality improvement justifies its latency and memory cost.
