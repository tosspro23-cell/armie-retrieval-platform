# ARMIE Retrieval Platform

An adaptive, production-oriented retrieval-platform reference implementation for knowledge-intensive AI systems. It keeps planning, execution, result refinement, evaluation, capability discovery, and offline policy evolution separate under the frozen architecture contract.

The first scenario is **Expert Discovery**—finding and ranking domain experts from semantic, lexical, metadata, and graph signals.

## v0.2.1 production validation

v0.2.1 validates the frozen v0.2 architecture with replaceable production implementations. It does not redesign the planner, runtime flow, registries, provider interfaces, contracts, or evaluation workflow.

- `OllamaStructuredLLMClient` is a configurable local `StructuredLLMClient`. It validates the configured model before it is used and gives a precise `ollama serve` / `ollama pull <model>` instruction when unavailable.
- `BGEEmbeddingProvider` defaults to `BAAI/bge-m3`, is configurable, and only loads already-local model weights. It never downloads a large embedding model automatically.
- Offline `VectorIndexBuilder`, `KeywordIndexBuilder`, and `GraphIndexBuilder` create separate persistent artifacts. Online retrievers load and query those artifacts; they never construct indexes at request time.
- `FaissDenseRetriever` uses a persisted FAISS index; `IndexedSparseRetriever` uses a persisted keyword index; the existing NetworkX graph provider now also loads a persisted graph artifact.
- Benchmark knowledge sources can be generated at 50, 200, or 500 experts and remain separate from generated indexes.
- Evaluation now reports Precision@K, Recall@K, MRR, NDCG@K, and latency.

The current local validation outcome is recorded in [Validation Report v0.2.1](docs/validation-report-v0.2.1.md). It confirms FAISS, keyword, graph, metrics, the installed Ollama planner, and BGE-M3 embeddings. Other environments still require an explicit local BGE-M3 download; see [Production prerequisites](#production-prerequisites).

## v0.2 highlights

- Configurable planners: `RuleBasedPlanner` and LLM-compatible `LLMPlanner` emit the same immutable `RetrievalPlan`.
- Production-style independent registries for retrievers, processors, and providers: capability metadata, version, priority, health status, discovery, and resolution.
- Dense-style, sparse, and Hybrid/RRF retrieval; first NetworkX graph-retrieval implementation for Expert Discovery.
- A shared `RetrievalRuntime`, ensuring every planner executes through the same downstream pipeline.
- Offline adaptive-learning MVP: immutable observations → rule-based optimisation → published, versioned policy. Runtime reads only the latest policy, never historical observations.
- Demonstration of Rule → Hybrid, LLM → Dense, and (when NetworkX is installed) LLM → Graph.

The frozen architectural boundaries are maintained in [Architecture Freeze v1.0](docs/architecture-freeze-v1.md). Release-level navigation is available through the [repository overview](docs/repository-overview.md), [engineering milestones](docs/engineering-milestones.md), [v0.2.1 release notes](docs/release-notes-v0.2.1.md), and [v0.2.1 validation report](docs/validation-report-v0.2.1.md).

## Architecture

```text
Runtime plane
Query -> Planner -> RetrievalPlan -> Retrieval Runtime -> RetrievalResult
                                                 -> ordered Result Processors -> Evaluation

Learning plane (offline)
ExecutionObservation + EvaluationResult -> Learning Engine -> Policy Repository
                                                        -> published policy for later runtime
```

`RetrievalPlan` stays declarative: it can request strategies, processors, parameters, filters, and constraints, but never names a provider, SDK, index, or API.

## Install and run

```bash
python3 -m pip install -e .
python3 examples/expert_discovery_demo.py
python3 -m unittest discover -s tests -v
```

The complete v0.2.1 dependency set is declared in `pyproject.toml`, `setup.cfg`, and `requirements.txt`.

## Production validation

Generate knowledge independently of indexes:

```bash
python3 examples/generate_benchmark_dataset.py --size 50 --output .artifacts/benchmark
```

Run the full offline validation fixture. It builds persistent FAISS, keyword, and NetworkX graph artifacts, exercises dense/sparse/hybrid/graph retrieval through the unchanged runtime, and writes a JSON report:

```bash
python3 examples/production_validation.py --size 50
```

The validation fixture uses a deterministic embedding test double only to verify the FAISS artifact lifecycle without downloading a multi-gigabyte model. It separately validates BGE-M3 when the model has already been installed locally.

## Production prerequisites

The default production configuration is in [`configs/production.yaml`](configs/production.yaml). It selects a local Ollama model and BGE-M3 without embedding any provider, SDK, index, or API details in a `RetrievalPlan`.

```bash
# Start Ollama and install the model selected in configs/production.yaml.
ollama serve
ollama pull qwen3:4b

# Explicitly prepare BGE-M3; the platform never downloads it on your behalf.
huggingface-cli download BAAI/bge-m3
```

Then compose the unchanged runtime with prebuilt artifacts using `ProductionArtifacts` and `create_production_platform`. The vector, keyword, and graph indexes must have been built offline first.

## Planner configuration

```yaml
planner:
  type: rule # or llm
```

The LLM planner accepts an injected `StructuredLLMClient` that returns structured plan data. The included demo uses a deterministic test double so it can run without credentials; substitute an API-backed client in deployment without altering downstream components.

## Deliberate MVP boundaries

- The in-memory provider and hashed dense-style embeddings remain available for portable demonstrations and deterministic tests; production selection is configuration/composition driven.
- NetworkX validates graph abstractions before a future Neo4j/Memgraph provider.
- The learning engine is intentionally offline and rule-based; it publishes policies, not prompt mutations or runtime-memory lookups.
- No component silently rewrites a retrieval plan. Fallbacks must be explicit execution policy and produce observations for later optimisation.
