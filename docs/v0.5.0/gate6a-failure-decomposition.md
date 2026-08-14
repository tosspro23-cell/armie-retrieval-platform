# Gate 6A — C1 Failure Decomposition

**Status:** Diagnostic analysis only; no runtime, benchmark, threshold, or
architecture changes.

Gate 6A uses the valid Gate 6M per-query artifact and the immutable v1.1
judgement universe. It does not rerun C0/C1/C2. The benchmark identity remains
`v0.5-constraint-extension-v1.1` with fingerprint
`6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb`.

## 1. C0 → C1 Top-5 decomposition

There are 230 C0 Top-5 slots. C1 removes 180 of them; 50 slots are unchanged.

| Removed candidate class | Count | % of removed | % of C0 slots |
|---|---:|---:|---:|
| Relevant + ineligible | 94 | 52.22% | 40.87% |
| Relevant + eligible | 30 | 16.67% | 13.04% |
| Irrelevant + ineligible | 47 | 26.11% | 20.43% |
| Irrelevant + eligible | 9 | 5.00% | 3.91% |
| **Total removed** | **180** | **100%** | **78.26%** |

Classification uses frozen `relevance_grade > 0` and frozen canonical
eligibility. It does not infer relevance from runtime scores.

Among C0 Top-5 candidates with `relevance_grade >= 2` and ineligible status,
there are 94 cases. All 94 are removed by C1; none survives in a C1 Top-5.
This is the intended hard-filter benefit, although the same C0 set also
contains 30 relevant-and-eligible candidates that disappear from C1.

## 2. NDCG loss

Thirty-three of 46 queries have lower C1 NDCG@5. Total descriptive loss is
23.2994 NDCG points (the sum of per-query C0 minus C1 NDCG deltas).

| Removed high-relevance class present in query | Queries | Descriptive loss | Share of loss |
|---|---:|---:|---:|
| Relevant + ineligible only | 20 | 12.9098 | 55.41% |
| Relevant + eligible only | 4 | 3.0000 | 12.88% |
| Both classes | 9 | 7.3896 | 31.72% |

These are descriptive associations, not causal attribution. In particular,
raw NDCG penalizes removal of relevant-but-ineligible items even when removal
is contractually correct. The loss also contains genuine loss of eligible
relevant candidates.

Representative loss cases:

| Query | Stratum | C0 NDCG | C1 NDCG | Observation |
|---|---|---:|---:|---|
| `v05-cq-001` | numeric | 1.0000 | 0.0000 | One grade-3 eligible candidate and four grade-3 ineligible candidates are removed; numeric native filter matches no indexed documents. |
| `v05-cq-010` | location | 0.7860 | 0.3156 | Categorical filter passes candidates, but eligible high-grade candidates are not all in the C1 Top-5. |
| `v05-cq-012` | seniority | 1.0000 | 0.0000 | Grade-3 eligible candidates are removed by the seniority predicate targeting an absent projection field. |

Full returned IDs, grades, eligibility, constraint states, and supply remain
available in `gate6m-results/gate6-per-query.json`.

## 3. Relevant-and-eligible loss audit

Across the C0 retrieved Top-10 diagnostic window, 85 candidates satisfy
`grade >= 2`, `eligible = true`, and are absent from the C1 Top-5.

An exploratory Elasticsearch ID-plus-filter probe classified them as:

| Diagnostic outcome | Count | Interpretation |
|---|---:|---|
| Native filter excludes candidate | 55 | False exclusion / projection mismatch in the frozen C1 path |
| Filter passes; candidate loses filtered rank | 30 | Filter correctness is intact, but filtered Dense ranking does not place the candidate in Top-5 |
| Compiler non-executable | 0 in this Top-10 set | No additional compiler rejection was observed in this probe |

The native-filter probe was diagnostic only. It did not change index contents,
runtime code, production settings, or benchmark artifacts.

The 55 false exclusions are concentrated in:

- `years_experience` → projection field `years_experience`, absent from the
  frozen dense-index mapping;
- ordered `seniority` → projection field `seniority_rank`, absent from the
  frozen dense-index mapping;
- multi-constraint queries containing either field.

By query stratum, the native-filter-exclusion count is: seniority 32,
multi-constraint-3plus 8, hard-negative 5, numeric 3, numeric-boundary 3,
multi-constraint 3, and unknown 1. These are projection/compiler-path
diagnostics, not new relevance labels.

Categorical fields (`industries`, `roles`, `locations`) were observable in the
index and passed the ID-plus-filter probe. The 30 filter-pass losses therefore
represent a separate ranking/retrieval problem, not a filter correctness
finding.

## 4. Exploratory eligible-conditioned metrics

These metrics are diagnostic only and do not replace Gate 6M promotion metrics.
For each query, the ideal list is restricted to relevant-and-eligible
judgements; NDCG uses that restricted ideal, Precision uses five returned
slots, and MRR is the first relevant-and-eligible item in the retrieved Top-10.
Queries without a relevant eligible judgement contribute zero to the relevant
metric denominator.

| Arm | Eligible NDCG@5 | Eligible Precision@5 | Eligible MRR | Existing Eligible Recall@10 | Existing Eligible Fill@5 |
|---|---:|---:|---:|---:|---:|
| C0 | 0.4161 | 0.3000 | 0.3947 | 0.0116 | 0.3730 |
| C1 | 0.2621 | 0.2174 | 0.2527 | 0.0092 | 0.2703 |
| C2-20 | 0.2605 | 0.2174 | 0.2509 | 0.0092 | 0.2703 |
| C2-50 | 0.2621 | 0.2217 | 0.2509 | 0.0092 | 0.2757 |
| C2-100 | 0.2621 | 0.2217 | 0.2509 | 0.0092 | 0.2757 |

The eligible-conditioned metrics still decline from C0 to C1. Therefore the
Gate 6M NDCG loss is not only an objective-mismatch artifact.

## 5. Query archetypes

| Archetype | Example | Evidence |
|---|---|---|
| Correct removal, good eligible replacement | `v05-cq-010` | C1 retains eligible results and returns two relevant eligible candidates, but fewer than C0's raw relevance ordering. |
| Correct removal, no relevant eligible replacement | `v05-cq-001` | C1 returns no results because the numeric filter has no matching indexed field. |
| False exclusion | `v05-cq-012` | Canonical principal candidates are eligible, but `seniority_rank` is absent from the dense projection. |
| Filter passes, ranking loss | `v05-cq-005` | Industry filter matches; several grade-3 eligible candidates at Dense ranks 6–10 do not enter C1 Top-5. |
| Genuine scarcity | `v05-cq-002` | Frozen canonical eligible supply is zero; no retrieval strategy can fill five eligible slots. |

## 6. Eligible Fill decline

Gate 6M Eligible Fill@5 falls from 0.3730 to 0.2703. The decomposition is
mixed:

- correct removal of relevant-but-ineligible candidates explains part of the
  raw list change;
- 55 relevant-and-eligible candidates in the diagnostic Top-10 are falsely
  excluded by missing projection fields;
- 30 relevant-and-eligible candidates pass the filter but lose filtered Dense
  ranking;
- genuine scarcity contributes for the nine supply-scarce queries.

The result is not attributable to a single clean objective mismatch.

## 7. C2 diagnostic recovery

Using only Gate 6M artifacts, C2-20 recovered no relevant-and-eligible
candidate absent from C1. C2-50 and C2-100 recovered one common candidate:

| Query | Candidate | Grade | Eligibility | C0 rank | C2-50/100 pool rank | C1 status | Fill impact |
|---|---|---:|---|---:|---:|---|---|
| `v05-cq-029` | `expert-v2-08347` | 3 | eligible | outside C0 Top-10 | 4 | absent from C1 Top-5 | raises query fill from 0.2 to 0.4; no material aggregate gain |

This does not satisfy the frozen C2 promotion rule and does not reopen C2
promotion.

## 8. Elasticsearch observations

The frozen C1 runtime used Elasticsearch 8.15.3 native `knn` with:

- `k = 10` and `size = 10` for the diagnostic candidate path;
- `num_candidates = 2 × k`;
- a native `knn.filter` containing the compiled contract DSL;
- filtering inside the approximate kNN request, before result return.

The index contains `industries`, `roles`, and `locations`, but the inspected
mapping does not contain `years_experience` or `seniority_rank`. This is direct
evidence for projection mismatch, not a claim about generic Elasticsearch ANN
behavior. For fields that do exist, the observed filter-pass/ranking-loss
cases are consistent with a different filtered ANN candidate set, but no
statistical ANN recall claim is made here.

## Scope and validity

All 46 queries are included. Gate 6M results and benchmark assets were not
modified. No runtime or threshold was changed. This is a diagnostic
decomposition, not a formal benchmark rerun.
