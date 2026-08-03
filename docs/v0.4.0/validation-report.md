# v0.4.0 Validation Report

## Checkpoint

Phase 1 was committed at `63ec012f5fb3a5d29093418fa6ddd757e3880c91` with
`feat: add v0.4.0 relevance engineering foundation`. Gate 2 and Gate 3 are
validation work after that checkpoint; this report does not declare v0.4.0
complete and does not cover Gate 4.

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

## Remaining scope

Gate 4, Query Lab graded-relevance UI, release preparation, tagging, and push
are intentionally out of scope for this checkpoint. Synthetic benchmark
judgements remain draft and require review before being treated as ground
truth.
