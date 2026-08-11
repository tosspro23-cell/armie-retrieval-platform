# Gate 5.5B Results

## Status

The dense-index prerequisite is **unblocked**. The full Dataset v2 build,
120-query contract audit, full judgement matrix, BM25 index, BGE-M3 dense index,
and matching FAISS artifact completed. H1–H4 comparison was not run in this
bounded blocker-resolution task.

| Profile | Required path | Result |
|---|---|---|
| H1 | Elasticsearch BM25 → metadata boost | Existing BM25 prerequisite; benchmark not executed |
| H2 | Elasticsearch dense → metadata boost | Unblocked; benchmark not executed |
| H3 | BM25 + dense → ARMIE RRF | Unblocked; benchmark not executed |
| H4 | BM25 + dense → BGE cross-encoder | Unblocked; benchmark not executed |

No v2 H1–H4 metric is reported because the benchmark was not executed here.
Candidate boundaries remain retrieval 100, fusion 100, rerank 30, final top-k 5,
RRF k 60. No v1/v2 architecture conclusion is claimed until the benchmark
executes; comparative cells remain **inconclusive**.

## Dense prerequisite evidence

- Model: `BAAI/bge-m3`, CPU, 1024 dimensions.
- Progressive builds: 100 (batch 4, 3.93 s), 1,000 (batch 4, 150.91 s), and
  10,000 (batch 8, 1,519.89 s); all completed with zero bulk failures.
- Elasticsearch index: `armie-experts-v1-v2-gate55b-dense-10000`, 10,000
  documents; `armie-experts-read` resolves to this index.
- FAISS artifact: 10,000 vectors, 1024 dimensions, persisted outside the repo.
- The earlier full-build termination produced no usable shell exit code or
  signal record, so an OOM cause is not asserted. The bounded builder now uses
  per-batch materialization, incremental vector persistence, identity-checked
  checkpoint/resume, and resource/device/bulk observability.
