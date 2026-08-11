# Dataset v2 Refinement Pilot Audit

Status: Gate 5.5A refinement only; not Gate 5.5B and not production-realistic.

## Identity and scope

- Dataset version: `v2-realism-pilot-r2`
- Profiles: 750; queries: 40; judgements: 30,000
- Document seed: 7301; query seed: 9137
- Generator: `expert-discovery-generator-v2-realism-0.2-r2`
- The previous `v2-realism-pilot` remains preserved for comparison.

## Previous vs refined pilot

| Metric | Previous v2 pilot | Refined r2 pilot |
|---|---:|---:|
| Normalized-summary duplicate rate | 1.47% | 0.27% |
| Near-duplicate pair rate | 0.0267% | 0.0007% |
| Query/document 3-gram overlap | 0.0000 | 0.0000 |
| Profiles with invalid temporal records | 0 | 0 |
| Positive judgement evidence coverage | 100% | 100% |

## Diversity and semantics

- Roles are distributed across 13 controlled roles; no role dominates (each is
  57–58 of 750 profiles).
- Seniority distribution: mid 173, senior 288, principal 289.
- Nine narrative families are balanced (83–84 profiles each); dominant opening
  frequency is 11.2%.
- Query semantic buckets: exact 30, partial 4, semantic 4, low-overlap indirect 2.
- All ten query categories have four queries and explicit semantic fields.
- Contract validation: all 40 queries valid; no language/structured-truth mismatches.
- Hard-negative query types: wrong relationship, advisory-only, outside-window and
  missing-skill (one query each).

## Negative and hard-negative metrics

The previous `hard_negative_density` value counted Grade-0 rows only within the
four hard-negative query slices: numerator = Grade-0 hard-negative rows;
denominator = 4 × 750 candidate rows. It conflated ordinary negatives with
structured near-misses and is retained only as `legacy_density` for traceability
(r2 value: 0.859000).

The refined rates use all 30,000 judgements as denominator:

- Negative judgement rate: **79.6800%** (23,904 / 30,000).
- True hard-negative judgement rate: **1.5633%** (469 / 30,000).
- Easy-negative rate: **78.1167%** (23,435 / 30,000).
- Hard-negative query count: **4**; candidate rows: **3,000**.
- True hard-negative types: advisory-only 94, missing-skill 94,
  outside-window 140, wrong-relationship 141.

Only canonical support plus a structured relationship, evidence, temporal or
controlled missing-skill near-miss is classified as a hard negative.

## Integrity and limitations

Gold judgements use canonical structured truth, relationships, temporal records
and evidence only. Silver remains explicitly rule-assisted. v1 is immutable.
The benchmark remains a **controlled synthetic relevance benchmark** with
templated language, controlled-vocabulary leakage risk, and no external human
ground truth. The v1 reference contains 9,496 duplicate normalized summaries
out of 10,000. Results must not be generalized to natural expert-network data.

The machine-readable r2 audit is generated outside the repository at
`/tmp/armie-v040-dataset-v2-pilot-r2/audit.json`.
