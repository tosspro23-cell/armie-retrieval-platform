# Gate 6D — Constraint-Aware Benchmark Results

**Protocol:** `v0.5-constraint-aware-eval-protocol-v1`
**Protocol fingerprint:** `7cfc4945cb81bfe145dc1d80d0e936f9e1e4d9bdc521f7254113cb4405156e12`
**Execution:** 230/230, repaired Gate 6B index, unchanged ANN settings

## Primary metrics

| Arm | Eligible NDCG@5 | Eligible P@5 | Eligible MRR | Eligible Recall@10 | Eligible Fill@5 | Satisfaction@5 | Violation@5 | Prohibited@5 | Hard-negative@5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 0.3027 | 0.2913 | 0.4019 | 0.0120 | 0.3622 | 0.3870 | 0.6130 | 1.0000 | 0.4174 |
| C1 | 0.4917 | 0.4913 | 0.5897 | 0.0211 | 0.6108 | 0.8261 | 0.0000 | 0.0000 | 0.0000 |
| C2-20 | 0.4917 | 0.4913 | 0.5897 | 0.0210 | 0.6108 | 0.8261 | 0.0000 | 0.0000 | 0.0000 |
| C2-50 | 0.4917 | 0.4913 | 0.5897 | 0.0211 | 0.6108 | 0.8261 | 0.0000 | 0.0000 | 0.0000 |
| C2-100 | 0.4917 | 0.4913 | 0.5897 | 0.0211 | 0.6108 | 0.8261 | 0.0000 | 0.0000 | 0.0000 |

## Raw diagnostic metrics

| Arm | Raw NDCG@5 | Raw P@5 | Raw Recall@10 | Raw MRR | Grade-3 Hit@5 |
|---|---:|---:|---:|---:|---:|
| C0 | 0.7286 | 0.7087 | 0.0041 | 0.8605 | 0.9565 |
| C1 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 |
| C2-20 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 |
| C2-50 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 |
| C2-100 | 0.4917 | 0.4913 | 0.0029 | 0.5897 | 0.7174 |

Raw metrics remain diagnostics. The primary objective shows C1 improving
eligible utility while removing constraint violations.

## Paired eligible-NDCG comparisons

On 37 supply-sufficient queries:

| Pair | Wins | Ties | Losses | Mean delta | Median delta |
|---|---:|---:|---:|---:|---:|
| C0 → C1 | 21 | 16 | 0 | +0.2350 | +0.1312 |
| C1 → C2-20 | 1 | 35 | 1 | 0.0000 | 0.0000 |
| C1 → C2-50 | 1 | 35 | 1 | 0.0000 | 0.0000 |
| C1 → C2-100 | 1 | 35 | 1 | 0.0000 | 0.0000 |

Eligible Recall comparisons are similarly positive for C0 → C1 (25 wins, 12
ties, 0 losses) and effectively tied for C1 → C2. No significance claim is
made.

## Constraint and latency observations

C1 removed 96 relevant-but-ineligible C0 results and left one relevant-eligible
removal in the repaired run. Prohibited and hard-negative intrusion fell to
zero. C1 warm p50/p95 E2E was 13.3/14.7 ms; C0 p50/p95 was 42.4/75.5 ms.
C2 warm p50/p95 was 20.9/22.7 ms (N=20), 40.8/44.9 ms (N=50), and
76.7/80.0 ms (N=100).

C2 produced no material eligible quality gain over C1 and does not justify its
latency cost.
