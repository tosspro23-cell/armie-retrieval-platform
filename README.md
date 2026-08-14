# ARMIE Retrieval Platform

## v0.5.0 Constraint-Aware Retrieval

v0.5.0 supports deterministic structured hard-constraint expert retrieval over
the approved field scope using native pre-filtered Dense retrieval with strict
no-relaxation semantics. C1 is the promoted constrained path: H2 Dense plus a
trusted `RetrievalContract` and native Elasticsearch pre-filter. C0 remains H2
Dense for unconstrained semantic retrieval. C2 is diagnostic/de-prioritized and
C3 is deferred.

Supported deterministic scope: `years_experience`, `industry`, `role`,
`location`, `seniority`, approved explicit exclusions, and approved
conjunctions. v0.5.0 does not provide arbitrary natural-language constraint
extraction, general temporal or relationship reasoning, delivery/evidence
qualification, graph retrieval, or C2/C3 production support.

Release-readiness evidence and reproducibility identity are in
[`docs/v0.5.0/gate8-release-readiness.md`](docs/v0.5.0/gate8-release-readiness.md),
[`docs/v0.5.0/v0.5.0-release-notes.md`](docs/v0.5.0/v0.5.0-release-notes.md), and
[`docs/v0.5.0/v0.5.0-release-manifest.json`](docs/v0.5.0/v0.5.0-release-manifest.json).

The v0.5.0 benchmark remains a controlled synthetic relevance benchmark, not
validated real-world expert-search quality.

## v0.4.0 Expert Discovery Relevance Engineering (historical baseline)

v0.4.0 is the **Expert Discovery Relevance Engineering Foundation**. It adds a reproducible relevance-engineering foundation while preserving the v0.3.0 Workbench and runtime. It provides typed `ExpertProfile` records, deterministic Dataset v2 manifests/checksums, 120 benchmark-query contracts, a 103 Gold / 17 Silver split, 0–3 judgements, graded metrics, failure taxonomy, experiment manifests, real Elasticsearch 8.15.3 BM25/dense adapters, FAISS comparison, ARMIE RRF, and BGE cross-encoder evaluation. Dataset v2 is a **controlled synthetic relevance benchmark**, not validated real-world expert-search quality: synthetic language and controlled-vocabulary leakage remain limitations; Gold is an independent structured audit, not external human ground truth. Results and limitations are documented in [`docs/v0.4.0/gate55b-results.md`](docs/v0.4.0/gate55b-results.md) and [`docs/v0.4.0/validation-report.md`](docs/v0.4.0/validation-report.md).

```bash
PYTHONPATH=src python3 examples/build_v040_dataset.py --size 10000
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Elasticsearch is local-only and optional for the deterministic foundation. Start it with `docker compose -f docker-compose.elasticsearch.yml up -d`; no Docker data volumes, secrets, or model weights are committed.

### Gate 6 Workbench Acceptance / Relevance Experiment UX

The local Workbench Query Lab exposes the frozen v2 benchmark library and the
shared H1–H4 runtime profiles. Reviewers can inspect Gold/Silver status,
structured constraints, evidence provenance, per-query graded metrics, timing,
and the benchmark manifest without treating one experiment as a new global
benchmark. Recall labels include their explicit denominator, and Gold remains
separate from rule-assisted Silver.

The Workbench requires generated v2 artifacts at `ARMIE_V2_BENCHMARK_ROOT`
(default `/tmp/armie-v040-dataset-v2-full`). Missing artifacts produce an
actionable backend-unavailable state; they are not copied into the repository.
This UX validates mechanics over the **controlled synthetic relevance
benchmark** and does not claim production expert-search quality or Gate 7
readiness.

## v0.3.0 Interactive Retrieval Workbench (historical baseline)

v0.3.0 adds a local, typed FastAPI workbench and React client on top of the existing runtime. It supports sessions and deterministic follow-ups, planner/reranker profiles, evidence cards, deterministic verification, complete trace inspection, and a Query Lab for labelled comparisons. The workbench delegates every query to `RetrievalRuntime` and the existing observability trace.

```bash
python3 -m pip install -e .
make workbench
# API: http://127.0.0.1:8000/docs
# UI:  http://127.0.0.1:5173
```

`make workbench` is the supported repository-local launcher. It exports the
checkout's `src/` directory before starting the API, so health and capability
diagnostics can report the package source path and current commit rather than
silently serving a stale globally installed package.

The editable install is the preferred development setup. For a repository-local diagnostic run, use `PYTHONPATH=src python3 -m uvicorn services.api.app:app --host 127.0.0.1 --port 8000`.

In the v0.5.0 Workbench, free queries default to `H2 — Dense` over the locally
available Dataset v2 projection and remain `unlabelled`; no benchmark quality
metrics are fabricated for free text. H1–H4 are explicit v0.4 profiles, while
the legacy v0.3 fixture profiles are labelled `Legacy` when selected. The UI
always shows the active dataset and profile identity.

The API is rooted at `/api/v1` (`/health`, `/capabilities`, `/sessions`, `/query`, `/traces/{trace_id}`, and `/query-lab/*`). See `docs/api-guide.md`, `docs/workbench-user-guide.md`, `docs/architecture-compliance-report-v0.3.0.md`, and `docs/release-notes-v0.3.0.md`.

An adaptive, production-oriented retrieval-platform reference implementation for knowledge-intensive AI systems. It keeps planning, execution, result refinement, evaluation, capability discovery, and offline policy evolution separate under the frozen architecture contract.

The first scenario is **Expert Discovery**—finding and ranking domain experts from semantic, lexical, metadata, and graph signals.

## v0.2.3 Model-Enhanced Retrieval

v0.2.3 adds explicit, profile-selected model components while retaining the deterministic baseline. It preserves the frozen runtime flow: planners emit declarative plans, retrievers execute them, result processors refine candidates, and evaluation remains observational.

| Profile | Planner | Reranker | Purpose |
|---|---|---|---|
| `fixture` | Rule-based | metadata boost | deterministic unit tests and CI |
| `baseline` | Rule-based | metadata boost | reproducible retrieval comparison |
| `model-enhanced` | Ollama | BGE Cross-Encoder | local model-assisted validation |

```bash
python3 examples/retrieval_trace_demo.py --profile baseline --query-id healthcare-azure-ai --verbose --export-json
python3 examples/retrieval_trace_demo.py --profile model-enhanced --query-id healthcare-azure-ai \
  --planner-model qwen3:4b --reranker-model BAAI/bge-reranker-v2-m3 --verbose
```

Provider selection is explicit: use `--planner rule-based|ollama` and `--reranker none|metadata|bge`. The trace records requested versus actual provider, configured model, controlled fallback, structured plan, timing, reranker scores, and rank changes. It never records hidden chain-of-thought. On macOS, the BGE Cross-Encoder runs in a JSON subprocess: FAISS remains in the main retrieval process and Torch remains in the worker, avoiding their conflicting OpenMP runtimes without `KMP_DUPLICATE_LIB_OK`.

### Planner routing diagnostics and model ablation

The Ollama prompt requests only finite structured labels alongside the plan: `reason_codes` (for example, `semantic_similarity_required` or `hybrid_signal_coverage`) and `constraint_types` (such as `skill`, `industry`, and `relationship`). These labels make a Dense-only decision inspectable without inventing a free-form explanation. The runtime uses `strategy` as the execution source of truth: in the current architecture, `hybrid` means **dense + sparse**; graph is selected through the separate `graph` strategy rather than as an arbitrary hybrid child.

Routing diagnostics are observational only. For example, a valid Dense-only semantic query is allowed; a plan that extracted multiple graph-representable constraints but did not select graph receives a warning and still executes exactly as declared.

```bash
python3 examples/planner_ablation.py \
  --mode full-pipeline --profile model-enhanced \
  --models qwen3:4b qwen3:8b \
  --reranker bge --reranker-model BAAI/bge-reranker-v2-m3 \
  --query-id healthcare-azure-ai --export-json
```

`--mode planner-only` reports only plan validity, extraction, strategy, routing warnings, fallback, and latency. `--mode full-pipeline` additionally executes retrieval and evaluation. It fingerprints one shared dataset and fixed execution context (indexes, candidates, RRF, reranker, evaluation, and fallback policy), so only the Planner model varies. It never changes the configured default automatically.

The candidate boundaries are separate and traceable: fusion output → `rerank_candidate_k` (20) → all reranker-scored candidates → `final_top_k` (5). The terminal order is **Query, Planner, Dense, Keyword, Graph, Fusion, Reranking, Final Ranking, Ground Truth, Evaluation, Timing, Warnings**. `planner_requested_top_k` is distinct from the effective runtime top K; precedence is **CLI override > explicit profile/runtime configuration > Planner requested value > default**. `sparse` and `keyword` are canonical aliases for routing validation.

`MetadataBoostReranker` is deterministic rules logic—`+0.05` for each exact metadata-filter match—not a neural semantic reranker. Its trace shows `metadata_candidates_processed`; only BGE shows Cross-Encoder, device, batch, and model-latency fields. Invalid structured Ollama fields produce actionable fallback diagnostics (field, expected/actual type, and reason), while retaining internal error details in JSON.

Reranker trace rows use `pre_rerank_rank`, `reranker_rank`, `rank_change`, and `rank_improvement`. The convention is `rank_change = reranker_rank - pre_rerank_rank`; therefore a move from 13 to 5 is `-8`. `rank_improvement` is the inverse, therefore `+8`. Both terminal and JSON output include all scored candidates, final membership, and explicit entered/exited Top-K states.

Graph retrieval remains **relevance-scored matching**, not strict logical `AND` filtering. Its trace surfaces expected, matched, and missing constraints, coverage, nodes, and edges. Evaluation reports Precision, Recall, and NDCG at K = 1, 2, 3, 5, 10, plus MRR and latency. With two labelled relevant experts, maximum Precision@5 is `2/5 = 0.4`; this is label-set arithmetic, not automatically a retrieval failure. The three-query synthetic benchmark validates mechanics, not real-world quality.

## v0.2.2 retrieval observability

v0.2.2 makes the established pipeline inspectable without changing its retrieval behaviour. An optional structured `RetrievalTrace` records the query, declarative plan, per-retriever candidates, RRF fusion, processors, final ranking, labelled ground-truth comparison, and the arithmetic behind evaluation metrics.

```text
Query → Planner → Retrievers → Fusion → Ranking → Evaluation
                                              ↓
                                      RetrievalTrace → Terminal / JSON
```

Trace collection is separate from presentation and uses no global mutable state. It never exposes hidden chain-of-thought: planner traces contain only the raw structured provider response where available, parsed plan, fallback decision, and operational metadata.

### Run a benchmark trace

```bash
python3 examples/retrieval_trace_demo.py \
  --query-id healthcare-azure-ai --verbose --export-json
```

The renderer shows Query, Planner, Dense Retrieval, Keyword Retrieval, Graph Retrieval, Fusion, Reranking, Final Ranking, Ground Truth, Evaluation, Timing Summary, and Warnings. Non-selected retrievers are explicitly shown as not selected.

### Run an arbitrary query or ablation

```bash
python3 examples/retrieval_trace_demo.py --query "Who knows Azure AI in healthcare?" --verbose
python3 examples/retrieval_trace_demo.py --query-id healthcare-azure-ai --mode dense
python3 examples/retrieval_trace_demo.py --query-id healthcare-azure-ai --mode keyword
python3 examples/retrieval_trace_demo.py --query-id healthcare-azure-ai --mode graph
python3 examples/retrieval_trace_demo.py --query-id healthcare-azure-ai --mode hybrid --export-json
```

JSON traces default to `.artifacts/traces/`, which is ignored by Git. The JSON schema is deliberately stable enough for later regression comparison, dashboards, notebooks, and UI rendering.

### Interpreting ground truth and metrics

Ground truth exists only for labelled benchmark queries. It distinguishes relevant retrieved experts (hits), relevant experts not retrieved (misses), and retrieved non-relevant experts (false positives). Interactive queries intentionally have no such labels.

- **Precision@K:** relevant retrieved results divided by K.
- **Recall@K:** relevant retrieved results divided by all labelled relevant experts.
- **MRR:** reciprocal of the first relevant rank; zero if none is retrieved.
- **NDCG@K:** discounted ranking quality against the ideal labelled order.
- **Latency:** retrieval execution time in milliseconds.

The three generated benchmark queries validate observability mechanics and component behaviour; they are a deterministic synthetic corpus, not evidence of real-world domain retrieval quality.

## v0.2.1 production validation

v0.2.1 validates the frozen v0.2 architecture with replaceable production implementations. It does not redesign the planner, runtime flow, registries, provider interfaces, contracts, or evaluation workflow.

- `OllamaStructuredLLMClient` is a configurable local `StructuredLLMClient`. It validates the configured model before it is used and gives a precise `ollama serve` / `ollama pull <model>` instruction when unavailable.
- `BGEEmbeddingProvider` defaults to `BAAI/bge-m3`, is configurable, and only loads already-local model weights. It never downloads a large embedding model automatically.
- Offline `VectorIndexBuilder`, `KeywordIndexBuilder`, and `GraphIndexBuilder` create separate persistent artifacts. Online retrievers load and query those artifacts; they never construct indexes at request time.
- `FaissDenseRetriever` uses a persisted FAISS index; `IndexedSparseRetriever` uses a persisted keyword index; the existing NetworkX graph provider now also loads a persisted graph artifact.
- Benchmark knowledge sources can be generated at 50, 200, or 500 experts and remain separate from generated indexes.
- Evaluation now reports Precision@K, Recall@K, MRR, NDCG@K, and latency.

The current local validation outcome is recorded in [Validation Report v0.2.3](docs/validation-report-v0.2.3.md). It confirms the deterministic production path, Ollama-driven full runtime execution, BGE-M3 availability, and controlled Cross-Encoder fallback when its weights are not cached.

## v0.2 highlights

- Configurable planners: `RuleBasedPlanner` and LLM-compatible `LLMPlanner` emit the same immutable `RetrievalPlan`.
- Production-style independent registries for retrievers, processors, and providers: capability metadata, version, priority, health status, discovery, and resolution.
- Dense-style, sparse, and Hybrid/RRF retrieval; first NetworkX graph-retrieval implementation for Expert Discovery.
- A shared `RetrievalRuntime`, ensuring every planner executes through the same downstream pipeline.
- Offline adaptive-learning MVP: immutable observations → rule-based optimisation → published, versioned policy. Runtime reads only the latest policy, never historical observations.
- Demonstration of Rule → Hybrid, LLM → Dense, and (when NetworkX is installed) LLM → Graph.

The frozen architectural boundaries are maintained in [Architecture Freeze v1.0](docs/architecture-freeze-v1.md). Release-level navigation is available through the [repository overview](docs/repository-overview.md), [engineering milestones](docs/engineering-milestones.md), [v0.2.3 release notes](docs/release-notes-v0.2.3.md), [v0.2.2 release notes](docs/release-notes-v0.2.2.md), and [v0.2.1 validation report](docs/validation-report-v0.2.1.md).

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

The complete v0.2.3 dependency set is declared in `pyproject.toml`, `setup.cfg`, and `requirements.txt`.

### v0.3.0 release validation

The Workbench is a local-first, single-user product surface over the existing runtime. It provides baseline and model-enhanced paths, an expandable trace Audit Trail, canonical trace-derived Evidence selection, deterministic Verification findings, execution/candidate-flow Metrics, and structured Query Lab comparison. Baseline final scores are labelled RRF/final baseline scores; model-enhanced final scores are labelled Cross-Encoder scores while retaining RRF contributions separately. Provider-specific scores are not directly comparable.

The release was browser-validated with **4 passed** tests using **Chromium via Playwright**. Known limitations are in-memory sessions, synthetic benchmark data, a short-lived Cross-Encoder worker, no streaming, authentication, or file upload, and no hosted production deployment.

## Production validation

### Dataset v2 realism pilot

Gate 5.5A adds a separate `expert-discovery-v2-realism` pilot. It keeps Dataset
v1 immutable, separates profile, query and judgement generation, and audits
surface diversity, relationships, temporal consistency, evidence provenance and
hard negatives. Build it with:

```bash
PYTHONPATH=src python3 examples/build_v040_dataset_v2_pilot.py
```

The pilot is a **controlled synthetic relevance benchmark**, not validated
real-world expert-search quality. The v1 corpus contains 9,496 duplicate
normalized summaries out of 10,000, templated synthetic language and
controlled-vocabulary leakage risk. Gold is an independent structured audit,
not external human ground truth; results must not be generalized to natural
expert-network data. See [`dataset-v2-design.md`](docs/v0.4.0/dataset-v2-design.md),
[`dataset-card-v2.md`](docs/v0.4.0/dataset-card-v2.md),
[`dataset-v2-pilot-audit.md`](docs/v0.4.0/dataset-v2-pilot-audit.md), and the
[`benchmark stability plan`](docs/v0.4.0/benchmark-stability-plan.md).

Generate knowledge independently of indexes:

```bash
python3 examples/generate_benchmark_dataset.py --size 50 --output .artifacts/benchmark
```

Run the full offline validation fixture. It builds persistent FAISS, keyword, and NetworkX graph artifacts, exercises dense/sparse/hybrid/graph retrieval through the unchanged runtime, and writes a JSON report:

```bash
python3 examples/production_validation.py --profile baseline --size 50
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
