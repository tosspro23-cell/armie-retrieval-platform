# v1/v2 Benchmark Stability Report

Gate 5.5B stability analysis remains pending the real Dataset v2 H1–H4 run.
The full v2 corpus, Gold/Silver contracts, BM25 index, BGE-M3 dense index, and
FAISS artifact are ready. Dense prerequisites are unblocked; no H1–H4 metrics
were produced in this bounded task.

| Conclusion | v1 finding | v2 evidence | Classification |
|---|---|---|---|
| Dense vs BM25 | Existing Gate 5 result | No v2 dense result | Inconclusive |
| Hybrid vs Dense | Existing Gate 5 result | No v2 dense result | Inconclusive |
| H4 vs H3 | Existing Gate 5 result | No v2 rerank result | Inconclusive |
| Organization / temporal / role queries | v1 category metrics | v2 judgement contracts only | Inconclusive |
| True hard-negative behaviour | v1 retrieval evidence | v2 structured rate 1.5623% | Inconclusive without intrusion metrics |

The absence of a result is an environment blocker, not evidence that v1
conclusions generalize or fail.
