# ARMIE Retrieval Platform v0.5.0 — Gate 6 Benchmark Design

**Status:** Gate 6 Run 1 invalid; repaired Gate 6R candidate locked; execution not started

**Positioning:** A controlled, versioned constraint-retrieval experiment over
the immutable Dataset v2 corpus. It is not a claim of natural expert-network
search quality.

## 1. Corpus and extension identity

The benchmark extension uses the same Dataset v2 full corpus and does not
modify profiles or the released v0.4 benchmark:

```yaml
dataset_manifest: v2-realism-full
profile_count: 10000
dataset_checksum: 514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc
benchmark_extension: v0.5-constraint-extension-v1.1
query_count: 46
gold_count: 46
silver_count: 0
scarcity_query_count: 9
contract_schema: v0.5-retrieval-contract-v1
projection: v0.5-constraint-projection-v1
gold_silver_governance: v0.4-compatible
top_k: 5
recall_k: 10
```

The materialized query, judgement and audit assets, including exact strata and
fingerprint, are recorded under
[`benchmark-extension-v1.1/`](benchmark-extension-v1.1/). The prior v1 assets
remain immutable historical materialization for invalid Gate 6 Run 1. The
index identity is an expected execution identity, not evidence that Gate 6R
has run.

Run 1 is retained as `INVALID_FOR_ARCHITECTURE_PROMOTION` because its
execution query text did not preserve the base semantic query and its negative
constraints were serialized in the wrong contract collection. The repaired
v1.1 lineage binds each extension query to an exact base query ID and uses
`RetrievalContract.exclusions` for prohibited requirements.

## 2. Stratified query extension

Each query is versioned separately from the immutable profiles and is paired
with an expected `RetrievalContract`. The extension must contain deterministic
cases for:

| Class | Required coverage |
|---|---|
| Numeric | `>=`, `between`, and boundary cases for years of experience |
| Categorical | Industry, role and location |
| Seniority | Equality, `>= senior`, and principal-only |
| Negative | Industry exclusion and `NOT_IN` |
| Multi-constraint | Industry + experience; industry + experience + seniority; role + exclusion; other conjunctions |
| Selectivity | Fewer than Top-K eligible candidates and starvation cases |
| Hard negatives | Near-misses with one structured violation |
| UNKNOWN / unsupported | Only where current deterministic architecture can represent the state |

Temporal, nested employer/client, relationship object/time, delivery/advisory
and prohibited-capability semantics are not silently fabricated into this
extension. They remain deferred until separately supported and approved.

## 3. Contract ground truth and governance

Every case records:

- natural semantic query;
- expected hard constraints, exclusions, operators and values;
- canonical field/category and policy;
- supported/deferred status;
- constraint evidence provenance;
- Gold or Silver tier.

For each query/candidate judgement, store separate fields for relevance,
eligibility, each constraint status (`SATISFIED`, `VIOLATED`, `UNKNOWN`),
violation reason and evidence. Gold is independent structured truth; Silver is
explicitly diagnostic/rule-assisted. Model-generated labels are not treated as
ground truth. Under strict policy, UNKNOWN does not satisfy a hard constraint
and is not silently relaxed.

Gate 6 evaluates manually constructed `RetrievalContract` objects unless a
separate extraction experiment is approved. Therefore it must not claim
natural-language contract-extraction performance.

## 4. Frozen benchmark arms

| Arm | Execution |
|---|---|
| C0 | H2 Dense |
| C1 | H2 Dense + deterministic native pre-filter |
| C2-20 | H2 Dense Top-20 + deterministic post-filter |
| C2-50 | H2 Dense Top-50 + deterministic post-filter |
| C2-100 | H2 Dense Top-100 + deterministic post-filter |

C3 is excluded. H1/H3/H4 are historical references only. All arms use the
same versioned queries, index, environment and Top-K.

## 5. Metrics and exact denominators

Standard relevance metrics remain unchanged: NDCG@5, Precision@5, Recall@10,
MRR and Grade-3 Hit@5. Each report must identify profile, tier, query slice
and candidate boundary; v0.4 metric semantics are not reinterpreted.

Constraint metrics are defined as follows:

- **Required Constraint Satisfaction@5:** returned Top-5 candidates satisfying
  every required hard constraint / returned Top-5 count.
- **Constraint Violation@5:** returned Top-5 candidates with at least one
  known hard violation / returned Top-5 count.
- **Prohibited Constraint Violation@5:** returned Top-5 candidates violating
  an explicit exclusion / returned Top-5 count.
- **True Hard-Negative Intrusion@5:** structured near-miss hard negatives in
  returned Top-5 / returned Top-5 count; ordinary unrelated negatives are not
  included.
- **Unknown Constraint Rate@5:** returned Top-5 candidates with an
  unverifiable required hard constraint / returned Top-5 count.
- **Eligible Recall@K:** relevant-and-eligible candidates retrieved in Top-K /
  all relevant-and-eligible candidates in that query's judgement contract.
  Gold and Silver denominators remain separate.
- **Strict Shortfall Rate:** executions where returned eligible count is below
  requested Top-K / all executions, with shortfall magnitude reported
  separately. No denominator is changed to hide starvation.

For every C2 arm additionally report N, eligible candidates found, eligible
yield (`eligible candidates found / N`), shortfall, original Dense ranks of
eligible results, returned IDs and saturation behaviour.

## 6. Latency methodology

Record per execution, with cold/warm state and Elasticsearch version and
environment identity:

- contract validation/planning;
- native filter compilation where applicable;
- Dense retrieval;
- C2 candidate verification;
- eligible Top-K assembly;
- end-to-end latency.

Report p50, p95 and mean where the sample supports them. Do not report a stage
that the runtime cannot observe. End-to-end latency must not be lower than the
included stage timings for the same sample. C2 latency must always be paired
with its explicit N.

## 7. Paired comparison and guardrails

All arms run on the same query IDs and environment. Report paired per-query
deltas, win/tie/loss, mean and median deltas, and bootstrap intervals only if
the stratum has sufficient sample size. Underpowered strata must be labelled
descriptively; no statistical significance claim is permitted without support.

Primary decision measures are Required Constraint Satisfaction@5,
Prohibited Constraint Violation@5 and True Hard-Negative Intrusion@5.
Guardrails are NDCG@5, Recall@10, Precision@5, MRR, Eligible Recall, latency
and strict shortfall.

The following decision protocol is frozen before execution. A paired bootstrap
95% interval is descriptive unless the query stratum has sufficient support;
underpowered strata remain explicitly non-significant.

- Promote C1 only if Required Constraint Satisfaction@5 improves over C0 and
  True Hard-Negative Intrusion@5 decreases, both with a positive directional
  paired estimate; at least 60% of queries are non-worse on each primary
  measure; and no guardrail (NDCG@5, Precision@5, Recall@10, MRR, Eligible
  Recall, Eligible Fill@5 or Retrieval Shortfall@5) degrades by more than 5
  percentage points. Warm p95 end-to-end latency may not increase by more than
  50%.
- Retain a C2 arm only if it recovers eligible recall or Eligible Fill not
  recovered by C1 with a positive paired direction and a practical gain in at
  least 10% of eligible-supply-sufficient queries, while satisfying the same
  5-point quality guardrail and no more than 2x C1 warm p95 latency. Otherwise
  C2 is de-prioritized.
- Any primary result with a mixed direction, an unsupported denominator, or a
  violated guardrail is exploratory and cannot promote an arm.

These are decision rules, not claims about expected outcomes, and cannot be
changed after viewing Gate 6 results without relabelling the experiment.

These same thresholds were defined before Gate 6 Run 1 and remain unchanged
for Gate 6R. The invalid Run 1 observations did not alter them.

## 8. Gate 6 execution sequence

1. Validate corpus checksum.
2. Validate projection and index identity.
3. Validate the benchmark manifest.
4. Validate expected contracts and Gold/Silver separation.
5. Execute C0.
6. Execute C1.
7. Execute C2-20.
8. Execute C2-50.
9. Execute C2-100.
10. Compute standard relevance metrics.
11. Compute constraint metrics and denominators.
12. Compute stage and end-to-end latency.
13. Produce paired comparisons.
14. Perform error and hard-negative analysis.
15. Apply the pre-registered architecture decision rules.

No step has been executed by this document.

## 9. Reproducibility and limitations

The result package must include the corpus checksum, extension and schema
versions, query/tier counts, category and hard-negative distributions,
projection/index identity, arm settings, Top-K, environment and seeds. The
benchmark remains a controlled synthetic relevance benchmark with the known
Dataset v2 limitations; it must not be generalized to natural expert-network
data. Gate 6 execution requires explicit authorization after this design
freeze.
