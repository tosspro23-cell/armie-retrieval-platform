# Gate 6B — Controlled Re-evaluation Results

## Aggregate metrics

| Arm | NDCG@5 | P@5 | Recall@10 | MRR | G3 Hit@5 | Satisfaction@5 | Violation@5 | Eligible Recall@10 | Eligible Fill@5 | E2E mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 0.7286 | 0.7087 | 0.0041 | 0.8605 | 0.9565 | 0.3870 | 0.6130 | 0.0117 | 0.3622 | 53.6 ms |
| C1 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 | 0.8261 | 0.0000 | 0.0211 | 0.6108 | 11.9 ms |
| C2-20 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 | 0.8261 | 0.0000 | 0.0211 | 0.6108 | 17.6 ms |
| C2-50 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 | 0.8261 | 0.0000 | 0.0211 | 0.6108 | 34.2 ms |
| C2-100 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 | 0.8261 | 0.0000 | 0.0211 | 0.6108 | 63.1 ms |

Gate 6M → Gate 6B C1 deltas:

- raw NDCG@5: `0.2191 → 0.4917` (+0.2727), still 23.69 percentage points
  below the repaired-run C0 baseline of 0.7286;
- Eligible Recall@10: `0.0092 → 0.0211`;
- Eligible Fill@5: `0.2703 → 0.6108`;
- total shortfall: `105 → 40`;
- mean E2E latency: `7.7 → 11.9 ms`;
- warm p50/p95 E2E: `13.0 / 14.4 ms` for repaired C1.

The repaired native filter eliminates the projection-related eligible loss.
The residual raw-NDCG gap is not a reason to change the frozen metric.

## Eligible-conditioned diagnostics

Using the same diagnostic denominators as Gate 6A:

| Arm | Eligible NDCG@5 | Eligible P@5 | Eligible MRR |
|---|---:|---:|---:|
| C0 | 0.3027 | 0.2913 | 0.4019 |
| C1 | 0.4917 | 0.4913 | 0.5897 |
| C2-20 | 0.4917 | 0.4913 | 0.5897 |
| C2-50 | 0.4917 | 0.4913 | 0.5897 |
| C2-100 | 0.4917 | 0.4913 | 0.5897 |

These are exploratory and do not replace raw Gate 6 promotion metrics. They
show that eligible retrieval is substantially healthier after projection
repair.

## Updated C0 → C1 decomposition

The repaired run removed 143 C0 Top-5 candidates:

| Class | Count |
|---|---:|
| Relevant + ineligible | 96 |
| Relevant + eligible | 1 |
| Irrelevant + ineligible | 45 |
| Irrelevant + eligible | 1 |

The relevant-and-eligible removal count is now **1**, compared with 30 in the
Gate 6M decomposition and 55 projection-related diagnostic exclusions in Gate
6A's broader Top-10 window. The remaining single case is not a projection
false exclusion.

## C2 and residual ranking

C2-20, C2-50, and C2-100 produced the same aggregate results as repaired C1.
They recovered no additional aggregate eligible quality. No promotion rule is
met for C2. A filtered-ANN tuning study is not warranted from this result alone.
