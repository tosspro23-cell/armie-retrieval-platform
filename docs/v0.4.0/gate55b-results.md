# Gate 5.5B Results

## Status

The dense-index prerequisite is **unblocked**. The full Dataset v2 build,
120-query contract audit, full judgement matrix, BM25 index, BGE-M3 dense index,
and matching FAISS artifact completed. H1–H4 comparison completed on the
frozen v2 Gold/Silver split after the dense unblock.

| Profile | Required path | Result |
|---|---|---|
| H1 | Elasticsearch BM25 → metadata boost | Executed on Gold and Silver |
| H2 | Elasticsearch dense → metadata boost | Executed on Gold and Silver |
| H3 | BM25 + dense → ARMIE RRF | Executed on Gold and Silver |
| H4 | BM25 + dense → BGE cross-encoder | Executed on Gold and Silver |

Candidate boundaries remain retrieval 100, fusion 100, rerank 30, final top-k
5, RRF k 60. Gold and Silver denominators are separate; Silver is rule-assisted
monitoring evidence, not Gold truth.

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

## Experiment manifest

- Checkpoint commit: `58baad41a49e61277de1c6fab1e3fad064fb1885`
- Dataset: `v2-realism-full`; checksum:
  `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
- Query set: `expert-discovery-queries-v2-realism-0.2`; judgement set:
  `expert-discovery-judgements-v2-realism-0.2`
- Elasticsearch: 8.15.3, green; BM25 physical index
  `armie-experts-v1-v2-gate55b-bm25-r2`; dense physical index
  `armie-experts-v1-v2-gate55b-dense-10000`
- Aliases: `armie-experts-read` points to dense for dense reads; BM25 is
  addressed by its physical index; write alias state was not used by the
  benchmark.
- Embedding: `BAAI/bge-m3`, 1024 dimensions, CPU; projection is the shared
  searchable-text projection used by ES and FAISS.
- FAISS: 10,000 × 1024 artifact fingerprint is recorded in the ignored
  validation manifest under `/tmp/armie-v040-dataset-v2-full-faiss`.
- Reranker: `BAAI/bge-reranker-v2-m3`, local BGE cross-encoder, warm batch size
  8; candidate boundaries retrieval 100, fusion 100, rerank 30, final top-k 5,
  RRF k 60.

## H1–H4 Gold results

| Profile | P@5 | Recall@10 | Recall@10 grade >=2 | MRR | NDCG@5 | Grade-3 Hit@5 | Grade-3 Hit@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| H1 | 0.6039 | 0.0058 | 0.0058 | 0.6246 | 0.6054 | 0.6311 | 0.6311 |
| H2 | 0.7534 | 0.0065 | 0.0065 | 0.8252 | 0.7569 | 0.8641 | 0.8641 |
| H3 | 0.7534 | 0.0072 | 0.0072 | 0.8061 | 0.7594 | 0.8155 | 0.8155 |
| H4 | 0.7495 | 0.0070 | 0.0070 | 0.8042 | 0.7596 | 0.8155 | 0.8155 |

Gold contains 103 queries across all ten categories; Silver contains 17
queries. Pairwise Gold NDCG@5 win/tie/loss: H1 vs H2 `16/57/30`, H2 vs H3
`16/63/24`, H1 vs H3 `7/67/29`, H3 vs H4 `17/71/15`. Mean deltas are -0.1515,
-0.0025, -0.1540, and -0.0002 respectively. No confidence interval or
significance claim was made. Full per-query traces and candidate provenance are
in the ignored artifact `/tmp/armie-v040-gate55b/gate55b-v2-benchmark.json`.

## Failure taxonomy snapshot

The existing classifier was applied to each returned top-k. Gold observations
were dominated by lexical mismatch in H1/H3/H4 and semantic false positives in
H2; delivery/mention ambiguity was flagged for all 12 delivery-oriented Gold
queries across profiles. Silver is diagnostic only and showed five lexical or
semantic retrieval failures per profile under the rule-assisted contract.
These labels separate retrieval-system observations from benchmark/data
limitations; they do not classify every Grade-0 judgement as a hard negative.
True hard-negative intrusion is measured from structured near-miss labels and
is distinct from ordinary unrelated negatives.

Gold true hard-negative intrusion in top-5 was H1 0/515, H2 3/515, H3 0/515,
and H4 0/515 returned slots (H2 cases were missing-skill near misses). Silver
monitoring showed 15/85 true near-miss intrusions for each profile, dominated by
the outside-window slice; this is rule-assisted diagnostic evidence only.
