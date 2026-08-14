# Gate 6M — Controlled Benchmark Results

**Status:** Valid metric repair; architecture recommendation: **C — Do not
promote C1 due to guardrail failure**

Gate 6M re-executed all 46 Gold queries across the five locked arms: 230/230
completed. Run 1 and Gate 6R remain preserved as historical invalid runs.

## Identity and environment

- Dataset: `v2-realism-full`, 10,000 profiles
- Checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
- Benchmark: `v0.5-constraint-extension-v1.1`
- Fingerprint: `6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb`
- Elasticsearch: 8.15.3 green
- Dense index: `armie-experts-v1-v2-gate55b-dense-10000`
- Embedding: `BAAI/bge-m3`
- Top-K / Recall-K: 5 / 10

## Aggregate metrics

| Arm | NDCG@5 | P@5 | Recall@10 | MRR | G3 Hit@5 | Satisfaction@5 | Violation@5 | Prohibited Violation@5* | Hard-negative intrusion@5 | Eligible Recall@10 | Eligible Fill@5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 0.7256 | 0.7087 | 0.0041 | 0.8533 | 0.9565 | 0.3870 | 0.6130 | 1.0000 | 0.4087 | 0.0116 | 0.3730 |
| C1 | 0.2191 | 0.2174 | 0.0011 | 0.2527 | 0.3043 | 0.3478 | 0.0000 | 0.0000 | 0.0000 | 0.0092 | 0.2703 |
| C2-20 | 0.2185 | 0.2174 | 0.0011 | 0.2509 | 0.3043 | 0.3478 | 0.0000 | 0.0000 | 0.0000 | 0.0092 | 0.2703 |
| C2-50 | 0.2214 | 0.2217 | 0.0011 | 0.2509 | 0.3043 | 0.3478 | 0.0000 | 0.0000 | 0.0000 | 0.0092 | 0.2757 |
| C2-100 | 0.2214 | 0.2217 | 0.0011 | 0.2509 | 0.3043 | 0.3478 | 0.0000 | 0.0000 | 0.0092 | 0.2757 |

\* Aggregate prohibited metric is over the four exclusion-bearing query cases
only: numerator = returned Top-5 items with an explicit exclusion marked
`VIOLATED`; denominator = 20 returned Top-5 slots (4 queries × 5). Non-
exclusion queries are query-level `not_applicable`, not zero-valued negatives.

## Scarcity and shortfall

- Legitimate scarcity: 9 queries
- Supply-sufficient: 37 queries

| Arm | Retrieval Shortfall@5 | Total shortfall magnitude |
|---|---:|---:|
| C0 | 0.6757 | 96 |
| C1 | 0.5676 | 105 |
| C2-20 | 0.5676 | 105 |
| C2-50 | 0.5676 | 105 |
| C2-100 | 0.5676 | 105 |

## Latency

| Arm | E2E mean | p50 | p95 | Contract p50 | C2 verification p50 |
|---|---:|---:|---:|---:|---:|
| C0 | 52.0 ms | 43.6 ms | 70.9 ms | 0.000 ms | — |
| C1 | 7.7 ms | 4.6 ms | 14.9 ms | 0.051 ms | — |
| C2-20 | 10.1 ms | 4.1 ms | 23.7 ms | — | 0.001 ms |
| C2-50 | 17.3 ms | 4.0 ms | 44.8 ms | — | 0.000 ms |
| C2-100 | 30.5 ms | 4.0 ms | 81.9 ms | — | 0.000 ms |

## Exclusion-bearing query audit

There are four exclusion queries: `v05-cq-013`, `v05-cq-014`, `v05-cq-036`,
and `v05-cq-037`.

| Arm | Exclusion-violating Top-5 | Generic ineligible Top-5 |
|---|---:|---:|
| C0 | 20 / 20 | 20 / 20 |
| C1 | 0 / 20 | 0 / 20 |
| C2-20 | 0 / 20 | 0 / 20 |
| C2-50 | 0 / 20 | 0 / 20 |
| C2-100 | 0 / 20 | 0 / 20 |

The audit preserves per-query returned IDs and exclusion states in
`gate6m-results/gate6-per-query.json`. It demonstrates that generic
ineligibility and explicit exclusion violation are distinct categories. The
generic `Violation@5` metric uses all returned Top-5 slots; it is not the
denominator for `Prohibited Violation@5`.

## Paired NDCG@5

| Pair | Win | Tie | Loss | Mean delta | Median delta |
|---|---:|---:|---:|---:|---:|
| C0 → C1 | 0 | 13 | 33 | -0.5065 | -0.4852 |
| C1 → C2-20 | 0 | 45 | 1 | -0.0005 | 0.0000 |
| C1 → C2-50 | 1 | 45 | 0 | +0.0023 | 0.0000 |
| C1 → C2-100 | 1 | 45 | 0 | +0.0023 | 0.0000 |

No significance claim is made.

## C2 and guardrails

C2-20 recovered two result-set differences beyond C1; C2-50 and C2-100 also
recovered two. No material aggregate Eligible Recall gain was observed. C2
saturated around N=50 while latency increased with N.

C1 eliminates known hard violations, but NDCG@5 drops from 0.7256 to 0.2191,
a degradation of approximately 50.65 percentage points, far beyond the frozen
5pp guardrail. Therefore C1 is not promoted. C2 is de-prioritized because it
does not add sufficient eligible-recall/fill value and costs more. C3 remains
deferred.
