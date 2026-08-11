# Dataset v2 Full Gate 5.5B Audit

Status: full corpus, contract audit, dense-index construction, and H1–H4
benchmark execution complete. This remains a controlled synthetic benchmark,
not a production-realism claim.

## Manifest

- Dataset: `expert-discovery-v2-realism`; version: `v2-realism-full`
- Profiles: 10,000; queries: 120; judgements: 1,200,000
- Seeds: document 7301; query 9137
- Checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
- Query contracts: 120/120 valid

## Quality

- Summary duplicate rate: 0.27%
- Near-duplicate pair rate: 0.0079% (3,982 exact Jaccard candidates)
- Invalid temporal records: 0
- Query/document phrase overlap: 0.022321
- Grades: 0 = 943,090; 1 = 101,412; 2 = 5,625; 3 = 149,873
- Negative judgement rate: 78.5908%
- True hard-negative rate: 1.5623%
- Easy-negative rate: 77.0285%
- True hard-negative types: wrong relationship 5,625; outside-window 5,625;
  missing-skill 3,750; advisory-only 3,748

## Index status

Elasticsearch 8.15.3 is green. BM25 index
`armie-experts-v1-v2-gate55b-bm25-r2` contains 10,000 documents with zero bulk
failures. BGE-M3 dense index
`armie-experts-v1-v2-gate55b-dense-10000` contains 10,000 documents with zero
bulk failures, 1024 dimensions, and model `BAAI/bge-m3`; the
`armie-experts-read` alias resolves to it. A matching FAISS artifact was built
outside the repository with 10,000 vectors and 1024 dimensions.

The earlier unbounded/full-process termination had no usable shell exit code or
signal record, so an OOM cause is not asserted. The bounded builder now
materializes one batch at a time, persists vectors incrementally, writes an
identity-checked checkpoint after every batch, and records device, RSS, elapsed
time, bulk outcomes, and vector counts. Progressive validation succeeded for
100 (batch 4, 3.93 s), 1,000 (batch 4, 150.91 s), and 10,000 (batch 8,
1,519.89 s) profiles on CPU with no bulk failures. RSS was approximately
2.0–2.7 GB after model load and stable in the 10,000 run.

This remains a **controlled synthetic relevance benchmark** with templated
language, controlled-vocabulary leakage risk, and Gold structured audit rather
than external human ground truth. The v1 corpus remains immutable and retains
9,496 duplicate normalized summaries out of 10,000. Neither dataset should be
generalized to natural expert-network data.

The full Dataset v2 corpus and all dense prerequisites are built. H1–H4 ran on
103 Gold and 17 Silver queries using the frozen runtime boundaries. See
`gate55b-results.md`, `benchmark-stability-report.md`, and
`architecture-decisions.md` for metrics and evidence-qualified conclusions.
