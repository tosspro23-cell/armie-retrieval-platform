# Benchmark Protocol

Gate 5 uses one fixed synthetic 10,000-profile dataset, query set
`expert-discovery-judgements-v1`/`v1`, and the real Elasticsearch index
`armie-experts-v1-gate23b-20260803`. The same BGE-M3 embedding model, candidate
boundaries (`100 / 100 / 30 / 5`) and ARMIE runtime are used for every profile.

Profiles are executed separately as H1 BM25, H2 Elasticsearch Dense, H3 BM25 +
Dense + ARMIE RRF, and H4 H3 + BGE Cross-Encoder. Index construction is
offline; retrievers consume the existing index only. Gold and Silver are never
merged into one unqualified score.

Every query record includes profile, returned IDs, judgement evidence, trace,
latency, failure codes and per-query metrics. The complete machine-readable
run is written by `examples/run_v040_gate5.py` to the configured output path;
the checked-in results document contains the measured aggregate and category
summary.

## Metric definitions

- **Precision@5:** binary relevant (`grade > 0`) hits in the first five divided by 5.
- **Recall@10:** binary relevant hits in the first ten divided by all labelled relevant profiles for that query.
- **Recall@10 grade >= 2:** the same calculation with grade 2/3 relevant and a grade 2/3 denominator.
- **Grade-3 Hit@10:** query-level indicator that a grade-3 result appears in the first ten.
- **Judged Recall@10:** standard binary Recall@10 over the complete judgement contract; it is reported separately to make the judged denominator explicit.
- **MRR:** reciprocal rank of the first binary relevant result in the first ten; zero when absent.
- **NDCG@5:** graded gain `2^grade - 1` at ranks 1–5, normalized by the ideal top five for that query.
- **Grade-3 hit rate:** query-level indicator that any grade-3 profile appears in Top-5.
- **Hard-negative intrusion rate:** query-level indicator that any grade-0 profile appears in Top-5 for a hard-negative query.
- **Required-constraint satisfaction:** grade-3 results in Top-5 divided by 5.
- **Prohibited-constraint violation:** Top-5 results carrying a prohibited constraint divided by 5.

Latency is reported separately as p50/p95. Provider-specific BM25, dense,
RRF and Cross-Encoder scores retain their own semantics and are not compared
as if they shared a scale. Trace timing fields are distinct: `retrieval` is the
retriever envelope, `dense`/`sparse` are source calls, `fusion` is the RRF
merge, `reranker_model_load` and `reranker_inference` are BGE stages,
`reranking` is their sum, and `end_to_end` is the measured request wall time.
For hybrid retrieval, fusion is included inside the retrieval envelope and is
not added a second time to produce end-to-end latency.

The Gate 5 end-to-end value is **trace-enabled request latency**. The existing
hybrid trace collector re-reads source results to expose source-level
contributions; therefore traced hybrid end-to-end latency includes that
observability overhead and must not be presented as an uninstrumented serving
SLO.
