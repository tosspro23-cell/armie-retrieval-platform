# ARMIE Retrieval Platform v0.2.3 — Model-Enhanced Retrieval

## Purpose

v0.2.3 validates configurable model-driven planning and semantic reranking while preserving Architecture Freeze v1.0 and the deterministic v0.2.2 baseline.

## Included

- Explicit fixture, baseline, and model-enhanced profiles.
- Rule-based or Ollama planner selection with observable requested/actual provider state and controlled fallback.
- No-op, metadata boost, and local BGE Cross-Encoder rerankers. The cross-encoder receives only a bounded candidate pool and requires locally prepared weights.
- Separate `retrieval_candidate_k`, `rerank_candidate_k`, and `final_top_k` plan parameters.
- Structured reranking/processor-stage traces, graph expected/matched/missing constraint coverage, and shared multiple-K metric calculations.
- Release-blocking observability patch for finite planner reason codes/constraint types, routing validation warnings, capability-aware terminal output, full Cross-Encoder score traces, and qwen3:4b/qwen3:8b planner-ablation reporting.
- Final consistency patch: reranking renders before final ranking; candidate selection, scoring, and final Top-K truncation are separately traced with exact stage warnings; reranker fields are provider-neutral.
- macOS OpenMP isolation path: FAISS stays in the parent process, while BGE/Torch runs in a structured JSON worker with response-ID, score, timeout, stderr, and controlled-fallback validation.
- Controlled ablation report: shared execution-context and plan fingerprints, plus explicit planner-only versus full-pipeline modes.

## Deliberate limits

- BGE Cross-Encoder weights are not bundled or downloaded automatically. A missing model follows the profile's configured deterministic fallback and emits explicit guidance.
- Graph retrieval is relevance-scored matching, not strict all-constraint intersection.
- The benchmark has three synthetic labelled queries and validates mechanics rather than real-world retrieval quality.
- No architecture, runtime, registry, provider, or contract redesign is included.
- `qwen3:8b` is not made the default by this release. A default change requires repeatable ablation evidence that compensates for additional latency and memory.

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 examples/production_validation.py --profile baseline
python3 examples/production_validation.py --profile model-enhanced --ollama-model qwen3:4b \
  --reranker-model BAAI/bge-reranker-v2-m3
```
