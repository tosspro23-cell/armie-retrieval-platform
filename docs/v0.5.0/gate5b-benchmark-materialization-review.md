# Gate 5B — Constraint Benchmark Materialization Review

**Status:** Materialized and protocol-locked; Gate 6 execution not started

Gate 5B created a separate v0.5 query/judgement extension over the immutable
Dataset v2 full corpus. It did not execute C0, C1 or C2, inspect comparative
retrieval results, modify runtime/Workbench, mutate Dataset v2, alter the
released v0.4 benchmark, or implement C3.

## 1. Materialized identity

| Field | Value |
|---|---|
| Dataset | `v2-realism-full` |
| Profiles | 10,000 |
| Dataset checksum | `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc` |
| Extension | `v0.5-constraint-extension-v1` |
| Queries | 46 |
| Gold / Silver | 46 / 0 |
| Scarcity queries | 9 |
| Judgements | 460,000 compressed JSONL rows |
| Benchmark fingerprint | `4c1982e1270d3052a29208359a9fcbf0f5fe8952a1282a796f74e931c2e51b18` |
| Contract schema | `v0.5-retrieval-contract-v1` |
| Projection | `v0.5-constraint-projection-v1` |
| Seeds | extension 50501; source document 7301; source query 9137 |

The machine-readable assets are in
[`benchmark-extension-v1/`](benchmark-extension-v1/), with the reproducible
builder at [`materialize_v050_constraint_extension.py`](../../scripts/materialize_v050_constraint_extension.py).
The fingerprint covers the ordered query contracts and compressed judgement
stream; any query, contract or judgement change produces a new fingerprint.

## 2. Exact strata

| Stratum | Count |
|---|---:|
| numeric experience | 4 |
| numeric boundary / BETWEEN | 4 |
| industry | 4 |
| role | 4 |
| location | 4 |
| seniority | 4 |
| exclusion / NOT_IN | 4 |
| two-constraint conjunction | 4 |
| three-plus conjunction | 4 |
| selective contracts | 4 |
| hard-negative near misses | 4 |
| UNKNOWN / support-diagnostic | 2 |

The extension deliberately avoids weighting the experiment around a single
`years_experience >= 20` slice. It contains 46 queries, with four cases in
each main stratum and two diagnostic UNKNOWN cases. All extension rows are
Gold because their contract and structured audit are explicit; no Silver tier
is mixed into the extension.

There are 4 hard-negative query strata and 62,020 structured near-miss
candidate judgements. These counts exclude ordinary unrelated Grade-0 rows.

## 3. Relevance and eligibility separation

Relevance is anchored to the immutable v2 structured judgement for each base
semantic query (`relevance_grade`); it is not recomputed from the added
constraint rules. Eligibility is independently evaluated against the expected
contract over every one of the 10,000 profiles. Each row preserves:

- `relevance_grade`;
- `eligible`;
- per-field `SATISFIED`, `VIOLATED` or `UNKNOWN` status;
- violation reason;
- hard-negative class;
- structured evidence provenance.

This design makes relevance and eligibility independently inspectable. It does
not claim external human ground truth: the corpus remains a controlled
synthetic relevance benchmark.

## 4. Denominators and scarcity

The judgement universe is exhaustive over the 10,000 materialized profiles, so
Eligible Recall@K is computable as:

`relevant AND eligible profiles retrieved in Top-K / all relevant AND eligible profiles in that query's 10,000-profile universe`.

For each query, **Eligible Supply** is the total relevant-and-eligible
population in that universe. **Legitimate Scarcity Rate** is queries with
Eligible Supply < 5 divided by 46; the materialized audit records 9 such
queries. **Retrieval Shortfall@5** is measured only among queries with supply
at least 5, as executions returning fewer than five eligible results divided by
eligible-supply-sufficient executions. **Shortfall Magnitude** remains `5 -
returned eligible count`. A strategy is not penalized for supply below five.

**Eligible Fill@5** is returned relevant-and-eligible candidates divided by
`min(5, Eligible Supply)`. For zero-supply queries it is `not_applicable`, not
zero, and the zero-supply count is reported separately.

## 5. Hard-negative governance

The extension only labels a hard negative when a candidate is semantically
relevant under the base judgement and fails at least one explicit structured
constraint. Ordinary unrelated Grade-0 candidates are not hard negatives.
The materialized audit reports the exact class/count distribution and keeps
the label separate from relevance and eligibility.

## 6. Gold/Silver and contract boundary

Gold independently audits semantic query, expected contract, relevance,
eligibility, constraint statuses, violation reason, hard-negative identity and
evidence provenance. Silver remains a diagnostic/rule-assisted tier in the
overall v0.4 governance model, but no Silver rows are included here.

Gate 6 evaluates correct manually constructed `RetrievalContract` objects. It
does not evaluate natural-language-to-contract extraction quality. Unsupported
or missing candidate values remain explicit rather than silently relaxed.

## 7. Frozen protocol

The formal arms remain C0, C1, C2-20, C2-50 and C2-100. C3 remains deferred.
The frozen metric definitions, latency stages, paired comparisons, 5-point
quality guardrail, 50% C1 latency guardrail and C2 retention rule are recorded
in [`gate6-benchmark-design.md`](gate6-benchmark-design.md). They were locked
before any arm execution.

## 8. Validation and stop condition

- Dataset checksum matches the supplied v2 full manifest.
- Query contracts are structurally complete and versioned.
- Gold/Silver is isolated (46 / 0).
- Eligibility is exhaustively evaluated over 10,000 profiles.
- Deterministic fixture denominator rules are encoded in the audit.
- Fingerprint is reproducible from the materialized assets.
- Local Markdown links and `git diff --check` pass.

Gate 5B is complete. Gate 6 may execute only after separate authorization;
this materialization did not run retrieval arms or comparative analysis.
