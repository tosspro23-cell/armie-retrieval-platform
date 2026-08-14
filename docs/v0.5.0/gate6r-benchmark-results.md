# Gate 6R — Formal Constraint Benchmark Re-execution Results

**Status:** **D — evidence remains invalid/inconclusive**

Gate 6R executed all 46 Gold queries across C0, C1, C2-20, C2-50 and C2-100
(230 executions) using the locked v1.1 asset. A new result-calculation defect
was discovered after execution: the result script computes
`Prohibited Constraint Violation@5` as any ineligible result, rather than only
results violating an explicit exclusion. That frozen metric is therefore not
independently interpretable for this run. Per the Gate 6R stop rule, no repair
or rerun was performed and no architecture promotion is made.

## Identity and environment

- Dataset: `v2-realism-full`, 10,000 profiles
- Dataset checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
- Benchmark: `v0.5-constraint-extension-v1.1`
- Fingerprint: `6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb`
- Queries / Gold / Silver: 46 / 46 / 0
- Judgements: 460,000
- Elasticsearch: 8.15.3, green
- Index: `armie-experts-v1-v2-gate55b-dense-10000`
- Embedding: `BAAI/bge-m3`, local CPU
- Top-K / Recall-K: 5 / 10

## Aggregate observations

| Arm | NDCG@5 | P@5 | Recall@10 | MRR | G3 Hit@5 | Satisfaction@5 | Violation@5 | Eligible Recall@10 | Eligible Fill@5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 0.7256 | 0.7087 | 0.0041 | 0.8533 | 0.9565 | 0.3870 | 0.6130 | 0.0116 | 0.3730 |
| C1 | 0.2191 | 0.2174 | 0.0011 | 0.2527 | 0.3043 | 0.3478 | 0.0000 | 0.0092 | 0.2703 |
| C2-20 | 0.2185 | 0.2174 | 0.0011 | 0.2509 | 0.3043 | 0.3478 | 0.0000 | 0.0092 | 0.2703 |
| C2-50 | 0.2214 | 0.2217 | 0.0011 | 0.2509 | 0.3043 | 0.3478 | 0.0000 | 0.0092 | 0.2757 |
| C2-100 | 0.2214 | 0.2217 | 0.0011 | 0.2509 | 0.3043 | 0.3478 | 0.0000 | 0.0092 | 0.2757 |

The displayed prohibited metric is invalid for this run and must not be used
as evidence. Unknown constraint rate was 0.0.

## Scarcity and shortfall

- Legitimate scarcity queries: 9
- Supply-sufficient queries: 37

| Arm | Retrieval Shortfall@5 | Total shortfall magnitude |
|---|---:|---:|
| C0 | 0.6757 | 96 |
| C1 | 0.5676 | 105 |
| C2-20 | 0.5676 | 105 |
| C2-50 | 0.5676 | 105 |
| C2-100 | 0.5676 | 105 |

Scarcity was excluded from retrieval-shortfall denominators. Eligible Fill is
computed against `min(5, eligible supply)` and zero-supply cases are not
treated as zero-quality results.

## Latency

| Arm | E2E mean | p50 | p95 | Contract p50 | Dense p50 | C2 verification p50 |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 67.6 ms | 42.6 ms | 104.9 ms | 0.000 ms | 42.6 ms | — |
| C1 | 7.0 ms | 4.1 ms | 13.9 ms | 0.051 ms | 4.0 ms | — |
| C2-20 | 9.6 ms | 3.5 ms | 23.0 ms | — | — | 0.001 ms |
| C2-50 | 17.5 ms | 3.5 ms | 47.4 ms | — | — | 0.000 ms |
| C2-100 | 30.1 ms | 3.5 ms | 83.5 ms | — | — | 0.000 ms |

Unobservable stages remain null; no fabricated timing was added.

## Paired NDCG@5 comparisons

| Pair | Win | Tie | Loss | Mean delta | Median delta |
|---|---:|---:|---:|---:|---:|
| C0 → C1 | 0 | 13 | 33 | -0.5065 | -0.4852 |
| C1 → C2-20 | 0 | 45 | 1 | -0.0005 | 0.0000 |
| C1 → C2-50 | 1 | 45 | 0 | +0.0023 | 0.0000 |
| C1 → C2-100 | 1 | 45 | 0 | +0.0023 | 0.0000 |

No significance claim is made.

## C2 recovery and hard negatives

C2-20 recovered two query-level result-set differences relative to C1;
C2-50 and C2-100 also recovered two. These were not shown to produce a valid
aggregate eligible-recall promotion. C2 saturation was effectively reached by
N=50 in this run. C2 latency increased with N.

The raw hard-negative intrusion fields are preserved, but the same
prohibited/ineligibility calculation defect prevents the required independent
exclusion analysis from being accepted as final evidence.

## Error classification and decision

The new defect is a **benchmark result-calculation defect**, not a runtime or
Dataset defect. It conflates general ineligibility with explicit exclusion
violation. No source code, labels, denominators or thresholds were modified
after seeing arm results.

**Final recommendation: D — Gate 6R evidence remains invalid/inconclusive.**

The next action requires a separate protocol-preserving repair of the metric
calculation and a new review before any rerun. Gate 7, Workbench and release
work remain out of scope.
