# ARMIE Retrieval Platform v0.4.0 — Expert Discovery Relevance Engineering Foundation

## What changed

- Dataset v2: 10,000 expert profiles, 120 query contracts, and isolated 103 Gold / 17 Silver evaluation tiers.
- Real Elasticsearch 8.15.3 BM25 and dense retrieval with BGE-M3 embeddings, plus a FAISS comparison artifact.
- H1 BM25, H2 Dense, H3 ARMIE RRF hybrid, and H4 hybrid + BGE cross-encoder profiles with frozen candidate boundaries.
- Graded relevance metrics, structured true-hard-negative analysis, and v1/v2 benchmark stability reporting.
- Relevance Experiment Workbench with structured constraint inspection, canonical evidence/provenance, per-query metrics, stage-aware latency, and browser acceptance validation.

## Key findings

- Dense materially outperformed BM25 on Dataset v2.
- Hybrid was near-tied with Dense in aggregate quality.
- Always-on BGE reranking added substantial local CPU latency with negligible aggregate gain over H3.
- Structured relationship, temporal, and prohibited constraints remain a separate deterministic systems concern.

## Known limitations

- Dataset v2 is a **controlled synthetic relevance benchmark** with templated language and possible controlled-vocabulary leakage.
- Gold is an independent structured audit, not external human relevance ground truth.
- Results are not natural expert-network validation and must not be generalized to natural expert-network data.
- Validation used local CPU inference and local Elasticsearch; no auth, multi-tenancy, cloud persistence, or production SLO claim is made.
- H4 reranking remains expensive and is not justified as an always-on default by current evidence.

The release does not claim production scale, universal retrieval superiority, a complete Knowledge Graph, automated learning-to-rank, or hosted deployment.
