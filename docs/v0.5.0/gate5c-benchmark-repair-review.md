# Gate 5C — Benchmark Semantic Repair Review

**Status:** Repaired Gate 6R candidate locked; retrieval execution not started

## 1. Run 1 lineage and root cause

Gate 6 Run 1 used benchmark v1 fingerprint
`4c1982e1270d3052a29208359a9fcbf0f5fe8952a1282a796f74e931c2e51b18` and is
preserved as `INVALID_FOR_ARCHITECTURE_PROMOTION`. Its execution text was a
standalone constraint description while relevance grades came from a different
base semantic query. Negative requirements were also placed in
`hard_constraints` as inverted operators rather than `exclusions`.

The failed artifacts remain under [`gate6-results/`](gate6-results/) and are
not overwritten by this repair.

## 2. Exact repair

The new v1.1 extension preserves all 46 queries and strata. Every query now
contains:

- `extension_query_id` (`query_id`);
- `base_query_id`;
- `base_semantic_query`;
- `constraint_overlay`;
- `execution_query_text` containing the base semantic intent plus overlay;
- `expected_retrieval_contract`;
- `relevance_judgement_source`.

Relevance is read only from the exact immutable base query ID. Eligibility is
recomputed independently over canonical profile truth. Negative requirements
are represented only in `RetrievalContract.exclusions`; positive requirements
remain in `hard_constraints`.

## 3. New identity

| Field | Value |
|---|---|
| Version | `v0.5-constraint-extension-v1.1` |
| Queries / Gold / Silver | 46 / 46 / 0 |
| Judgements | 460,000 |
| Fingerprint | `6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb` |
| Scarcity queries | 9 |
| Supply-sufficient queries | 37 |
| Hard-negative candidates | 62,020 |

The fingerprint is deterministic and changes if queries, contracts or
judgements change. The exact strata distribution remains four per main stratum
and two UNKNOWN diagnostic cases, as documented in Gate 5B.

## 4. Alignment and exclusion validation

Deterministic validation proves:

- every base query ID exists in the immutable v2 query asset;
- relevance source ID exactly equals base query ID;
- base semantic text is included in execution text;
- overlay fields equal the union of positive constraints and exclusions;
- negative queries have an empty positive constraint set and explicit exclusions;
- relevance and eligibility are independently represented;
- hard negatives require relevance >= 2 plus an actual `VIOLATED` status;
- scarcity uses relevant-and-eligible supply.

Changing a base query ID fails lineage validation. Exclusion polarity is tested
through the same explicit status model used by Gate 2/3; no inverted positive
shortcut remains.

## 5. Recomputed governance

Hard-negative counts and supply/scarcity metadata were recomputed from aligned
relevance plus unchanged eligibility truth. The old Run 1 count is not reused
as authority, even though this deterministic repair currently yields the same
aggregate count. Run 1 values remain historical only.

The pre-registered C1/C2 thresholds are unchanged: 60% non-inferior queries,
5pp relevance guardrail, C1 warm p95 +50% maximum, C2 10% supply-sufficient
gain rule and C2 <=2x C1 warm p95. No threshold was changed after Run 1.

## 6. Validation

- Gate 5C semantic repair tests: 6 passed.
- Fingerprint materialization repeated twice: identical.
- Query/judgement row count: 46 / 460,000.
- Markdown links: pass.
- `git diff --check`: pass.
- C0/C1/C2 retrieval: not run.

Gate 6R may execute only after separate authorization. No retrieval result from
Run 1 is used to promote an architecture.
