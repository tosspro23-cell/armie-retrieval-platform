# ARMIE Retrieval Platform

An adaptive, production-oriented retrieval-platform reference implementation for knowledge-intensive AI systems. It keeps planning, execution, result refinement, evaluation, capability discovery, and offline policy evolution separate under the frozen architecture contract.

The first scenario is **Expert Discovery**—finding and ranking domain experts from semantic, lexical, metadata, and graph signals.

## v0.2 highlights

- Configurable planners: `RuleBasedPlanner` and LLM-compatible `LLMPlanner` emit the same immutable `RetrievalPlan`.
- Production-style independent registries for retrievers, processors, and providers: capability metadata, version, priority, health status, discovery, and resolution.
- Dense-style, sparse, and Hybrid/RRF retrieval; first NetworkX graph-retrieval implementation for Expert Discovery.
- A shared `RetrievalRuntime`, ensuring every planner executes through the same downstream pipeline.
- Offline adaptive-learning MVP: immutable observations → rule-based optimisation → published, versioned policy. Runtime reads only the latest policy, never historical observations.
- Demonstration of Rule → Hybrid, LLM → Dense, and (when NetworkX is installed) LLM → Graph.

The frozen architectural boundaries are maintained in [Architecture Freeze v1.0](docs/architecture-freeze-v1.md). The exact v0.2 scope is recorded in [Engineering Milestone v0.2](docs/engineering-milestone-v0.2.md). Release-level navigation is available through the [repository overview](docs/repository-overview.md), [engineering milestones](docs/engineering-milestones.md), [release notes](docs/release-notes-v0.2.0.md), and [Architecture Compliance Report](docs/architecture-compliance-report-v0.2.0.md).

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

`networkx` is the only non-standard-library dependency and is required for the graph demonstration. All non-graph capabilities remain runnable without it; graph tests are skipped with an explicit reason when it is absent.

## Planner configuration

```yaml
planner:
  type: rule # or llm
```

The LLM planner accepts an injected `StructuredLLMClient` that returns structured plan data. The included demo uses a deterministic test double so it can run without credentials; substitute an API-backed client in deployment without altering downstream components.

## Deliberate MVP boundaries

- The in-memory provider and hashed dense-style embeddings preserve portability and deterministic tests.
- NetworkX validates graph abstractions before a future Neo4j/Memgraph provider.
- The learning engine is intentionally offline and rule-based; it publishes policies, not prompt mutations or runtime-memory lookups.
- No component silently rewrites a retrieval plan. Fallbacks must be explicit execution policy and produce observations for later optimisation.
