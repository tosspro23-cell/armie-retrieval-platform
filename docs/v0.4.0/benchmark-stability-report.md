# v1/v2 Benchmark Stability Report

## Dataset v2 execution

Gold contains 103 queries (all ten categories); Silver contains 17 queries and
is reported only as rule-assisted monitoring evidence. Gold metrics use only
`draft_gold_structured_audit` judgements; Silver uses only
`draft_silver_rule_assisted` judgements. The v2 corpus has 10,000 profiles and
the same frozen candidate boundaries: retrieval 100, fusion 100, rerank 30,
final top-k 5, RRF k 60.

| Profile | Gold P@5 | Gold Recall@10 | Gold MRR | Gold NDCG@5 | Grade-3 Hit@5 |
|---|---:|---:|---:|---:|---:|
| H1 BM25 + metadata | 0.6039 | 0.0058 | 0.6246 | 0.6054 | 0.6311 |
| H2 Dense + metadata | 0.7534 | 0.0065 | 0.8252 | 0.7569 | 0.8641 |
| H3 Hybrid RRF + metadata | 0.7534 | 0.0072 | 0.8061 | 0.7594 | 0.8155 |
| H4 Hybrid + BGE | 0.7495 | 0.0070 | 0.8042 | 0.7596 | 0.8155 |

Recall denominators are the per-query Gold relevant sets at grade >=1; the
very low global values reflect 10,000-profile denominators and must not be
read as a claim that only the displayed top-10 candidates were judged.

## Timing semantics

Values are trace stage timings, not interchangeable end-to-end measures.

| Profile | Retrieval mean (ms) | Fusion mean (ms) | Reranker inference mean (ms) | Total reranking mean (ms) | End-to-end mean (ms) |
|---|---:|---:|---:|---:|---:|
| H1 | 9.2 | 0 | 0 | 0 | 18.6 |
| H2 | 169.1 | 0 | 0 | 0 | 393.1 |
| H3 | 176.7 | 0.44 | 0 | 0 | 714.4 |
| H4 | 176.5 | 0.45 | 981.5 | 986.0 | 1,696.9 |

The raw machine-readable benchmark contains per-query timing values. H4 cold
model-load time was measured separately in the reranker trace; warm inference
is approximately 981 ms mean. End-to-end includes retrieval, fusion, reranking,
and trace/runtime overhead. No cold value is substituted for warm p50/p95.

Gold p50/p95 (ms): H1 retrieval 8.9/11.8, end-to-end 18.1/22.1; H2 retrieval
168.6/177.2, end-to-end 392.1/402.5; H3 retrieval 177.3/184.7, fusion
0.4/0.5, end-to-end 711.6/754.9; H4 retrieval 175.4/185.5, fusion 0.4/0.5,
warm reranker inference 970.2/1,092.5, total reranking 970.2/1,092.5, and
end-to-end 1,681.3/1,844.7.

## Pairwise Gold NDCG@5

| Comparison | Win / Tie / Loss | Mean delta (left−right) | Median delta |
|---|---:|---:|---:|
| H1 vs H2 | 16 / 57 / 30 | -0.1515 | 0.0000 |
| H2 vs H3 | 16 / 63 / 24 | -0.0025 | 0.0000 |
| H1 vs H3 | 7 / 67 / 29 | -0.1540 | 0.0000 |
| H3 vs H4 | 17 / 71 / 15 | -0.0002 | 0.0000 |

Bootstrap confidence intervals were not calculated; no significance claim is
made. Category samples, especially multi-constraint (2 Gold queries) and hard
negative (6 Gold queries), are too small for category-level significance.

## Stability classification

| Question | v1/v2 classification | Implication |
|---|---|---|
| Dense vs BM25 | strengthened on v2 | retain BM25 baseline; dense is useful on this distribution |
| Hybrid vs Dense | weakened / near tie | require complementary-value evidence before defaulting to hybrid |
| H4 vs H3 | inconclusive, near tie | BGE cost needs stronger quality gain |
| organization and temporal constraints | inconclusive | deterministic filtering/graph evidence needed |
| role/seniority and negative constraints | inconclusive | structured semantics remain under-enforced |
| employer/client and delivery/mention ambiguity | strengthened as risk | improve structured constraint handling before model expansion |
| graph/relationship modelling | inconclusive | target relationship-specific retrieval experiments only |

The v2 result is a controlled synthetic benchmark outcome and must not be
generalized to natural expert-network data.
