# v0.4.0 Validation Report

## Checkpoint

Phase 1 was committed at `63ec012f5fb3a5d29093418fa6ddd757e3880c91` with
`feat: add v0.4.0 relevance engineering foundation`. Gate 4 was checkpointed at
`86aed2d57938abcd3ed1e5f1af19cb10b646892d` with
`feat: validate hybrid retrieval and cross-encoder reranking`. Gate 5 is
validation work after that checkpoint; this report does not declare v0.4.0
complete.

## Deterministic foundation

- `PYTHONPATH=src python3 -m unittest discover -s tests -q`: 45 passed before
  the conditional integration checks were added.
- `(cd apps/workbench && npm test)`: 4 passed.
- `(cd apps/workbench && npm run build)`: passed.
- `python3 -m build`: produced the 0.4.0 sdist and wheel successfully.
- `git diff --check`: passed.
- Deterministic 10,000-record dataset: checksum
  `9f595cb7c84f6fc2b2a2a691526f86ccdb6f96e4675f8ce002ac0e5466689291`.
- Query taxonomy: 120 queries and 30,000 transparent draft judgements.

## Docker prerequisite evidence

The required environment checks passed on 2026-08-03:

- Docker `29.6.2`; Compose `v5.3.1`.
- Docker context `desktop-linux`, healthy Docker Desktop daemon.
- `docker pull hello-world` succeeded.
- `docker run --rm hello-world` succeeded.

The pinned `docker.elastic.co/elasticsearch/elasticsearch:8.15.3` image was
started by `docker compose -f docker-compose.elasticsearch.yml up -d`.

## Gate 2 — real Elasticsearch BM25 and indexing

**Status: passed.**

- Cluster endpoint: `http://127.0.0.1:9200`.
- Elasticsearch version: `8.15.3`.
- Cluster status: `green`, one node.
- Versioned index: `armie-experts-v1-gate23b-20260803`.
- Indexed documents: `10,000`; bulk response reported `rejected: 0`.
- Mapping version: `expert-discovery-es-mapping-v1`.
- Dense field: `dims=1024`, `index=true`, `similarity=dot_product`.
- Read and write aliases point only to the versioned index; write alias is
  explicitly marked as the sole write index.
- Real BM25 samples returned 10 candidates for each tested query. Examples:
  `Find experts with Elasticsearch experience` returned a top score of
  `16.446089`; the healthcare/Azure query returned a top score of `40.32179`;
  a filtered healthcare/RAG query returned 10 results.
- Online BM25 retrieval consumed the existing index; no query-time index build
  occurred.

## Gate 3 — Elasticsearch dense versus FAISS

**Status: passed.**

Both indexes were generated from the same 10,000 profiles, the same search
projection, and the locally available `BAAI/bge-m3` model (1024 dimensions).
The persistent FAISS artifact was loaded from `/tmp/armie-v040-faiss-gate3`;
Elasticsearch used the real indexed dense-vector field.

Across ten representative benchmark queries (top-10):

- Mean overlap: `8.7/10`.
- Mean Jaccard: `0.778`.
- Mean Spearman rank correlation over shared top-10 items: `0.798`.
- Mean Elasticsearch latency: `173.821 ms`.
- Mean FAISS latency: `40.446 ms`.
- Per-query overlap ranged from `7` to `10`; the semantic paraphrase query
  reached `10/10` overlap.

These are measured runtime values from the local services, not fabricated or
mocked metrics. Rank ordering differed in several cases, as expected from
FAISS exact inner-product search versus Elasticsearch's indexed HNSW dense
vector implementation.

## Conditional integration tests

`tests/test_v040_elasticsearch_integration.py` contains two opt-in checks for
the real pinned cluster and dense mapping. They are skipped by default so the
normal unit suite remains Docker-independent. Run them with:

```bash
ARMIE_RUN_ELASTICSEARCH_INTEGRATION=1 \
ARMIE_ELASTICSEARCH_TEST_INDEX=armie-experts-v1-gate23b-20260803 \
PYTHONPATH=src python3 -m unittest tests.test_v040_elasticsearch_integration -v
```

With that command's environment enabled, the full suite ran **47 tests, all
passing**, including both real Elasticsearch integration checks. Without the
environment flag, the normal suite ran **47 tests, 45 passed and 2 skipped**.

## Remaining scope before Gate 5

Query Lab graded-relevance UI, release preparation, tagging, and push remain
out of scope. Synthetic benchmark judgements require explicit tiering and
review before being treated as ground truth.

## Gate 4 — Hybrid Fusion and Cross-Encoder Validation

**Status: execution validated; relevance superiority not claimed.**

Gate 4 was executed after checkpoint commit
`2281f166ca40b5f7904ef9d5dcad0d4e1e976a2b` using the existing
`RuleBasedPlanner`, `RetrieverRegistry`, `ProcessorRegistry`,
`RetrievalRuntime`, `TraceCollector`, and BGE reranker pathway. No second
runtime or benchmark-only fusion path was introduced.

### Profiles

| Profile | Runtime path | Actual components |
|---|---|---|
| H1 | Rule Planner → BM25 → metadata boost → final Top-K | Elasticsearch BM25, `metadata_boost` |
| H2 | Rule Planner → dense → metadata boost → final Top-K | Elasticsearch dense kNN, `metadata_boost` |
| H3 | Rule Planner → BM25 + dense → ARMIE RRF → metadata boost → final Top-K | Elasticsearch BM25 + dense, `elasticsearch_hybrid`, `metadata_boost` |
| H4 | Rule Planner → BM25 + dense → ARMIE RRF → BGE Cross-Encoder → final Top-K | Elasticsearch BM25 + dense, `elasticsearch_hybrid`, `bge-reranker-v2-m3` |

All profiles used these declared boundaries:

```text
retrieval_candidate_k = 100
fusion_candidate_k    = 100
rerank_candidate_k    = 30
final_top_k           = 5
rrf_k                 = 60
```

### Real query set

Seven controlled queries were run per profile: exact skill, skill plus
industry, delivery/project experience, organization experience, semantic
paraphrase, multi-constraint, and hard-negative/ambiguity.

Sample real results for `Find experts with Elasticsearch experience`:

- H1 Top-5: `expert-00003, expert-00011, expert-00019, expert-00035, expert-00043`.
- H2 Top-5: `expert-02011, expert-09123, expert-06003, expert-09003, expert-06403`.
- H3 Top-5: `expert-00123, expert-00163, expert-00139, expert-00363, expert-00003`.
- H4 Top-5: `expert-00123, expert-00099, expert-09123, expert-00059, expert-08995`.

### Fusion evidence

H3 and H4 both executed 100 BM25 and 100 dense candidates, fused to 100
deduplicated canonical `expert_id` candidates, then passed exactly 30 to the
reranker. A sample H3 fused candidate recorded:

```text
expert-00123
  BM25:  rank=13, score=16.446089, semantic=elasticsearch_bm25_score,
         RRF contribution=0.0136986301
  Dense: rank=10, score=0.81085825, semantic=elasticsearch_dense_score,
         RRF contribution=0.0142857143
  total fused score=0.0279843444
```

Raw BM25 and dense scores were preserved as provider-specific signals and were
not normalized or directly compared. Deduplication used only canonical
`expert_id`.

### Cross-Encoder evidence

H4 used the locally available `BAAI/bge-reranker-v2-m3` model with no model
download. Every query passed exactly 30 candidates to the BGE Cross-Encoder,
processed 30, and returned final Top-5. The first measured request reported a
cold model-load latency of approximately `789.36 ms` and inference latency of
`226.25 ms`; subsequent warm requests reported `0 ms` model-load latency and
inference latencies from `165.42` to `223.70 ms`. Cold model loading is not
mixed into warm inference timing.

For the sample exact-skill query, `expert-00099` moved from pre-rerank rank 24
to rank 2 (`rank_change=-22`) and entered final Top-5. Trace records include
requested/actual reranker, model ID, candidate bounds, pre/post ranks, rank
movement, final membership, score semantics, and fallback diagnostic.

No fallback was used in the validated H4 run. The existing explicit fallback
path remains available and records provider, reason, and diagnostic when a
configured reranker fails; it does not mutate the immutable plan.

### Gate 4 commands and results

```bash
PYTHONPATH=src python3 examples/run_v040_gate4.py \
  --index armie-experts-v1-gate23b-20260803 \
  --output /tmp/armie-v040-gate4.json
# H1, H2, H3, H4 completed; output written to /tmp/armie-v040-gate4.json

PYTHONPATH=src python3 -m unittest discover -s tests -q
# 51 tests, 48 passed, 3 skipped (after Gate 4 tests were added)

ARMIE_RUN_ELASTICSEARCH_INTEGRATION=1 \
ARMIE_ELASTICSEARCH_TEST_INDEX=armie-experts-v1-gate23b-20260803 \
PYTHONPATH=src python3 -m unittest discover -s tests -q
# 51 tests passed, including real Elasticsearch Gate 2/3 checks and the
# real H1-H4 Gate 4 integration test
```

Frontend tests/build and the earlier package build remain unchanged and
passed. `git diff --check` passed after the Gate 4 changes.

## Gate 5 — Benchmark Validity, Gold Review, Relevance and Failure Analysis

**Status: completed; benchmark limitations remain explicit.**

Gate 5 ran 35 stratified Gold queries and 85 lower-confidence Silver queries
against the same 10,000-profile dataset, real Elasticsearch index, embedding
model, candidate boundaries and runtime used by Gate 4. Gold labels were
independently audited against structured source evidence and record reviewer,
status, rationale and correction history. Silver retained rule-assisted labels
and was never merged with Gold.

The audit found 9,496 duplicate normalized summaries and highly templated
language, with high synthetic vocabulary leakage risk. These limitations are
documented in `docs/v0.4.0/dataset-card.md`; Gate 5 is therefore a controlled
synthetic relevance benchmark, not validated real-world expert-search quality
and not a claim of production expert-network relevance.

Measured Gold NDCG@5 was H1 `.686`, H2 `.754`, H3 `.762`, H4 `.818`; Gold
required-constraint satisfaction was `.663`, `.737`, `.731`, `.811`. H4 Gold
warm Cross-Encoder inference was approximately 851.4 ms p50 after a 457.9 ms
cold model load; end-to-end p50 was 1,976.7 ms. The quality gain is therefore a
selective-latency trade-off. Negative and
temporal constraints remained weak, while organization retrieval improved with
Dense/Hybrid evidence. Pairwise win/tie/loss and category results are in
`docs/v0.4.0/gate5-results.md`; per-query traces, judgements and failure
evidence are emitted by `examples/run_v040_gate5.py`.

Gate 5 identified delivery/mention ambiguity, lexical mismatch, semantic false
positives and candidate-pool misses, plus relationship/provenance gaps that
justify future graph work. No statistical significance or generalization claim
is made. Query Lab, Gate 6/7, release preparation, tagging and push remain
out of scope.

## Gate 5.5A — Dataset v2 Realism Pilot

### Human-review refinement (r2)

After the original machine quality gates passed, qualitative review identified
role concentration, repeated sentence skeletons, taxonomy mismatches, weak
hard-negative examples and suspicious Grade 1 cases. The bounded r2 pilot
addresses those issues without starting Gate 5.5B: 750 profiles, 40 queries,
30,000 structured judgements, balanced role/seniority and narrative families,
explicit category constraints, a low-overlap semantic bucket and typed hard
negatives. It remains a **controlled synthetic relevance benchmark**; no claim
of production realism or external human ground truth is made.

**Status: pilot quality gate only; full H1–H4 was not rerun.**

The v2 identity is `expert-discovery-v2-realism`. Its document/profile, query
and judgement builders are independent pipelines with separate seeds and
surface lexicons. They share only canonical ontology identifiers and structured
truth. The judgement builder reads canonical relationships, temporal records and
evidence provenance, never generated search text or retrieval results.

The pilot is explicitly a **controlled synthetic relevance benchmark**. The v1
corpus remains immutable and retains 9,496 duplicate normalized summaries out of
10,000, templated synthetic language and controlled-vocabulary leakage risk.
Gold is an independent structured audit, not external human ground truth. Neither
dataset should be generalized to natural expert-network data.

The machine-readable audit and manual inspection sample are emitted by
`examples/build_v040_dataset_v2_pilot.py` to the ignored pilot output directory.
The tracked design and stability documents define the required next gate; no
production-realism claim is made here.

## Gate 5.5B checkpoint

The full Dataset v2 corpus (10,000 profiles, 120 queries and 1,200,000
judgements), BM25 index, BGE-M3 dense index, and matching FAISS artifact are
built. Query contracts validate 120/120. The dense prerequisite is now
unblocked; H1–H4 and v1/v2 stability claims remain intentionally unexecuted in
this bounded task. See `gate55b-results.md` for progressive build evidence and
the exact limitation on the earlier uninstrumented process termination.
