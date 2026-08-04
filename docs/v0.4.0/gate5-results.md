# Gate 5 Relevance Results

Run: 2026-08-04, real Elasticsearch 8.15.3, BGE-M3 embeddings, index
`armie-experts-v1-gate23b-20260803`, candidate boundaries `100 / 100 / 30 / 5`.
Profiles H1–H4 used the same planner, registry, runtime, trace and evaluation
path. Gold and Silver were executed separately.

## Global metrics

Values are query means. Precision/recall are binary with independent
grade-threshold diagnostics; NDCG is graded. The complete per-query timing and
metric records are in the generated machine-readable Gate 5 result.

| Tier | Profile | P@5 | R@10 | MRR | NDCG@5 | G3 hit | Hard-negative intrusion | Required constraints | Prohibited violations | End-to-end p50/p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Gold | H1 BM25 | .777 | .0009 | .829 | .686 | .714 | .171 | .663 | .086 | 315.1 / 320.4 |
| Gold | H2 Dense | .834 | .0011 | .834 | .754 | .829 | .171 | .737 | .086 | 388.7 / 399.4 |
| Gold | H3 Hybrid RRF | .846 | .0011 | .914 | .762 | .829 | .171 | .731 | .086 | 1110.7 / 1132.2 |
| Gold | H4 Hybrid+BGE | .840 | .0011 | .864 | .818 | .886 | .200 | .811 | .086 | 1976.7 / 2065.0 |
| Silver | H1 BM25 | .878 | .0012 | .891 | .879 | .635 | .118 | .607 | .024 | 318.5 / 329.0 |
| Silver | H2 Dense | .953 | .0014 | .953 | .953 | .682 | .047 | .682 | .024 | 386.1 / 396.8 |
| Silver | H3 Hybrid RRF | .929 | .0013 | .947 | .932 | .682 | .118 | .659 | .024 | 1118.2 / 1137.9 |
| Silver | H4 Hybrid+BGE | .920 | .0013 | .947 | .924 | .682 | .141 | .656 | .024 | 1981.7 / 2126.9 |

Gold is the decision tier. Silver is reported for monitoring only because its
labels remain rule-assisted.

Gold recall diagnostics were: H1 `Recall@10 grade>=2=.0024`,
`Grade-3 Hit@10=.714`; H2 `.0046`, `.829`; H3 `.0030`, `.829`; H4 `.0092`,
`.886`. `Judged Recall@10` is deliberately identical to standard binary
Recall@10 here because every profile in each tier has a judgement contract;
the metric is retained to make that denominator explicit. Queries with no
grade-3 result expose `no_grade_3_result=1` and do not become false positives.

## Gold category findings

- Exact skill, delivery/project and semantic-paraphrase queries were strong
  across all profiles.
- Organization queries were a BM25 failure (H1 NDCG 0.000); Dense and Hybrid
  helped, while H4 reached 0.908 NDCG.
- Multi-constraint queries were difficult: H1/H2/H3 NDCG .143/.372/.189;
  H4 improved to .835.
- Temporal queries remained weak (.485/.044/.339/.249 NDCG for H1–H4).
- Negative-constraint queries were unresolved (0.000 NDCG for all profiles).

## Pairwise Gold comparison

Win/tie/loss is based on per-query NDCG@5: H1 vs H2 `5/24/6`, H1 vs H3
`4/27/4`, H3 vs H4 `4/26/5`. These are descriptive comparisons; no
statistical significance is claimed.

## Timing scope and reranker trade-off

H4 used 30 candidates. The corrected timing contract reports retrieval,
fusion, reranker model-load, reranker inference, total reranking and
end-to-end independently. Retrieval is the retriever envelope; for hybrid it
includes the small RRF merge, while end-to-end is the measured request wall
time and includes processing. The final measured stage values were:

| Tier | Profile | Retrieval p50/p95 ms | Fusion p50/p95 ms | Cold model load ms | Warm inference p50/p95 ms | Warm total reranking p50/p95 ms | End-to-end p50/p95 ms |
|---|---|---:|---:|---:|---:|---:|---:|
| Gold | H1 | 97.4 / 103.1 | 0 / 0 | 0 | 0 / 0 | 0 / 0 | 315.1 / 320.4 |
| Gold | H2 | 169.8 / 177.3 | 0 / 0 | 0 | 0 / 0 | 0 / 0 | 388.7 / 399.4 |
| Gold | H3 | 248.1 / 256.0 | .49 / .61 | 0 | 0 / 0 | 0 / 0 | 1110.7 / 1132.2 |
| Gold | H4 | 247.2 / 269.0 | .51 / 2.01 | 457.9 | 851.4 / 929.7 | 851.4 / 929.7 | 1976.7 / 2065.0 |
| Silver | H4 | 245.0 / 257.7 | .53 / 2.10 | 512.2 | 866.5 / 962.8 | 866.5 / 962.8 | 1981.7 / 2126.9 |

The earlier approximately 243ms H4 value was retrieval-only and was not an
end-to-end value. End-to-end here is trace-enabled: the existing hybrid trace
collector re-reads source results to expose source-level contributions, so the
hybrid end-to-end values include observability overhead and are not raw serving
SLOs. H4 improved Gold NDCG and required-constraint satisfaction, but increased
hard-negative intrusion and did not consistently win per-query against H3.
This supports selective, high-value use rather than unconditional reranking.

## Failure analysis

Gold failures were dominated by delivery/mention ambiguity (28 classified
events), lexical mismatch (10), semantic false positives (5), and candidate
pool misses (3). The remaining material patterns were employer/client
ambiguity, temporal/negative constraint gaps and hybrid/reranker rank changes;
these are recorded per query in the machine-readable run, with expected IDs,
returned IDs, evidence and failure stage.

The principal remediation is better structured provenance and relationship
modelling, not simply larger candidate pools. Graph work is justified for
employer/client relationships, delivery provenance and temporal validity.

## Reproducibility

```bash
PYTHONPATH=src python3 examples/run_v040_gate5.py \
  --dataset /tmp/armie-v040-dataset-full \
  --index armie-experts-v1-gate23b-20260803 \
  --output /tmp/armie-v040-gate5
```

Gate 5 stops here. Query Lab, Gate 6/7 and release work remain out of scope.
