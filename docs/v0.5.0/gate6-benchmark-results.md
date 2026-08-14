# Gate 6 — Formal Constraint Benchmark Results

**Status:** Executed, but **invalid/inconclusive for architecture promotion**

The locked Gate 5B protocol was executed against all 46 Gold queries and all
five frozen arms. The raw results are preserved, but benchmark-asset defects
were discovered during analysis:

1. The materialized query text used for retrieval is a constraint-only
   natural-language string, while its relevance grades are anchored to a
   different base semantic query. Standard relevance comparisons therefore do
   not measure the intended query meaning.
2. Negative constraints were serialized as hard `not_in` constraints rather
   than the separate `exclusions` contract field, so the prohibited-violation
   metric is not independently interpretable in this run.

Results are not silently repaired or reinterpreted. A protocol-preserving
re-materialize and re-execution is required before promotion.

## 1. Identity and environment

- Dataset: `v2-realism-full`, 10,000 profiles
- Dataset checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
- Benchmark: `v0.5-constraint-extension-v1`
- Queries / Gold / Silver: 46 / 46 / 0
- Judgements: 460,000
- Fingerprint: `4c1982e1270d3052a29208359a9fcbf0f5fe8952a1282a796f74e931c2e51b18`
- Elasticsearch: 8.15.3, green local cluster
- Dense index: `armie-experts-v1-v2-gate55b-dense-10000`
- Embedding: `BAAI/bge-m3`, 1024 dimensions, local CPU model
- Top-K / Recall-K: 5 / 10
- Executions: 230 (46 × 5)

Raw per-query execution records, aggregate metrics and environment identity are
in [`gate6-results/`](gate6-results/). They include returned IDs, scores,
eligibility, constraint statuses, hard-negative IDs, supply, shortfall and
observable latency stages.

## 2. Aggregate results

| Arm | NDCG@5 | Precision@5 | Recall@10 | MRR | G3 Hit@5 | Satisfaction@5 | Violation@5 | Hard-negative intrusion@5 | Eligible Recall@10 | Eligible Fill@5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 | 0.1412 | 0.1478 | 0.0007 | 0.2282 | 0.4130 | 0.3652 | 0.6348 | 0.1043 | 0.0022 | 0.0541 |
| C1 | 0.0453 | 0.0435 | 0.0003 | 0.0868 | 0.1522 | 0.3478 | 0.0000 | 0.0000 | 0.0021 | 0.0541 |
| C2-20 | 0.0448 | 0.0435 | 0.0002 | 0.0826 | 0.1522 | 0.3478 | 0.0000 | 0.0000 | 0.0019 | 0.0541 |
| C2-50 | 0.0448 | 0.0435 | 0.0002 | 0.0826 | 0.1522 | 0.3478 | 0.0000 | 0.0000 | 0.0019 | 0.0541 |
| C2-100 | 0.0448 | 0.0435 | 0.0002 | 0.0826 | 0.1522 | 0.3478 | 0.0000 | 0.0000 | 0.0019 | 0.0541 |

Unknown constraint rate was 0.0 in this corpus. All table values are preserved
as raw observations only; they are not promotion evidence because of the
semantic query/relevance mismatch and exclusion-field defect. In particular,
Prohibited Constraint Violation@5 must not be interpreted as a valid standalone
metric for this run.

## 3. Scarcity and shortfall

- Frozen scarcity queries: 9
- Supply-sufficient queries: 37

| Arm | Retrieval Shortfall@5 | Total shortfall magnitude |
|---|---:|---:|
| C0 | 0.7838 | 102 |
| C1 | 0.5676 | 105 |
| C2-20 | 0.5676 | 105 |
| C2-50 | 0.5676 | 105 |
| C2-100 | 0.5676 | 105 |

Scarcity queries were not penalized in Retrieval Shortfall. Eligible Fill uses
`returned relevant-and-eligible / min(5, supply)` and is not applicable for
zero-supply queries.

## 4. Latency

All values are warm/steady execution observations from the same local run;
the first model-load event was excluded by model validation before execution.
Stage fields not observable in the current runtime are `null`, never inferred.

| Arm | E2E mean ms | E2E p50 ms | E2E p95 ms | Contract p50 ms | Dense/filter p50 ms | C2 verification p50 ms |
|---|---:|---:|---:|---:|---:|---:|
| C0 | 63.0 | 29.2 | 162.2 | 0.000 | 29.1 | — |
| C1 | 8.0 | 4.6 | 14.7 | 0.056 | 4.5 | — |
| C2-20 | 10.3 | 4.0 | 24.5 | — | — | 0.001 |
| C2-50 | 18.0 | 3.8 | 52.5 | — | — | 0.001 |
| C2-100 | 32.1 | 3.9 | 95.0 | — | — | 0.001 |

The C2 E2E cost generally rises with N. Native and post-filter stage timings
are not directly comparable because the provider currently exposes different
stage boundaries.

## 5. Paired comparisons

NDCG@5 win/tie/loss (second arm versus first):

| Pair | Win | Tie | Loss | Mean delta | Median delta |
|---|---:|---:|---:|---:|---:|
| C0 → C1 | 3 | 28 | 15 | -0.0960 | 0.0000 |
| C1 → C2-20 | 0 | 45 | 1 | -0.0005 | 0.0000 |
| C1 → C2-50 | 0 | 45 | 1 | -0.0005 | 0.0000 |
| C1 → C2-100 | 0 | 45 | 1 | -0.0005 | 0.0000 |

No confidence intervals or significance claims are made for this invalidated
execution.

## 6. C2 recovery and error analysis

C2 returned an additional ID relative to C1 in four query cases at all three
pool sizes. These were ordering/retrieval differences, not a demonstrated
eligible-recall promotion under a valid relevance contract. C2 aggregate
eligible recall and fill were not higher than C1. No C2 arm changed the frozen
constraint correctness metrics.

The primary error class is **benchmark/judgement contract mismatch**: retrieval
used the extension's constraint-only query text, while relevance grades came
from a different base semantic query. A second asset defect encoded negative
requirements in the wrong contract collection, conflating general
ineligibility with prohibited violations. These are benchmark asset defects,
not runtime repair opportunities. Secondary observations include semantic
retrieval misses and C2 candidate-pool cost. No benchmark labels or runtime
semantics were changed after viewing results.

## 7. Guardrails and validity

C1 eliminated known hard violations, but its NDCG@5 degradation versus C0 was
approximately 9.6 percentage points, exceeding the frozen 5-point guardrail.
The result therefore would fail promotion even without the semantic mismatch.
However, the mismatch makes the comparison invalid for a final architectural
decision. C2 did not meet the frozen retention rule in this run.

**Final Gate 6 recommendation: D — benchmark evidence is invalid/inconclusive
and requires protocol-preserving re-execution.**

Gate 6 does not promote C1, retain C2, or reopen C3. No Workbench or release
work begins from this result.
