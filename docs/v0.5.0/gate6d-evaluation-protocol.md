# Gate 6D — Constraint-Aware Evaluation Protocol v1

**Protocol ID:** `v0.5-constraint-aware-eval-protocol-v1`
**Protocol fingerprint:** `7cfc4945cb81bfe145dc1d80d0e936f9e1e4d9bdc521f7254113cb4405156e12`

This protocol changes evaluation governance, not benchmark identity or runtime
behavior. The benchmark remains `v0.5-constraint-extension-v1.1`, with 46 Gold
queries, 460,000 judgements, and fingerprint
`6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb`.

## Objective

Maximize semantic relevance **subject to** all supported hard constraints being
satisfied. Hard eligibility is a feasibility condition, not a soft relevance
preference.

Raw relevance remains observable as an unconstrained reference, but constrained
eligible relevance is the primary objective.

## Primary metrics and denominators

- **Eligible NDCG@5:** gain is computed only for candidates that are both
  relevant under frozen judgements and eligible under the RetrievalContract;
  the ideal list uses the same relevant-and-eligible universe. Ineligible
  candidates contribute zero usable gain.
- **Eligible Precision@5:** returned relevant-and-eligible candidates divided
  by returned Top-5 count.
- **Eligible MRR:** reciprocal rank of the first returned
  relevant-and-eligible candidate.
- **Eligible Recall@10:** retrieved relevant-and-eligible candidates in Top-10
  divided by all relevant-and-eligible candidates in the full 10,000-profile
  judgement universe.
- **Eligible Fill@5:** returned relevant-and-eligible divided by
  `min(5, eligible supply)`. Zero-supply queries are `not_applicable`.
- **Required Constraint Satisfaction@5:** returned eligible divided by returned
  Top-5 count.
- **Constraint Violation@5:** returned ineligible divided by returned Top-5
  count.
- **Prohibited Constraint Violation@5:** explicit exclusion violations divided
  by applicable returned Top-5 slots; non-exclusion queries are not applicable.
- **True Hard-Negative Intrusion@5:** returned structured hard negatives divided
  by returned Top-5 count.

Unknown constraint rate remains reported where applicable and is not collapsed
into eligible relevance.

## Diagnostic metrics

Raw NDCG@5, raw Precision@5, raw Recall@10, raw MRR, and Grade-3 Hit@5 remain
unconstrained relevance reference metrics. They are not the primary promotion
blocker for a hard-constraint system.

## Frozen C1 promotion rule

All conditions must hold:

1. Constraint Violation@5 is materially lower than C0, with at least 50%
   relative reduction; Prohibited Violation@5 is ≤1% where applicable; true
   hard-negative intrusion is materially lower; and no systematic false
   exclusion exists.
2. C1 is non-inferior to C0 on every primary eligible metric, with maximum
   degradation of 0.05 absolute points for Eligible NDCG, Precision, MRR,
   Recall, and Fill.
3. At least 60% of supply-sufficient queries are non-inferior using the same
   0.05 query-level eligible-NDCG tolerance.
4. Warm p95 E2E latency is no more than 1.5× C0.
5. Canonical eligible candidates have zero systematic native-filter exclusion.

These deterministic tolerances are frozen before execution. They are practical
engineering effect-size rules for 46 queries, not statistical significance
claims, and were selected as explicit tolerances rather than to guarantee a
pass.

## C2 and C3

C2 remains secondary and is retained only if it produces material eligible
quality gains on a meaningful fraction of supply-sufficient queries that justify
added latency. C3 remains deferred and can reopen only for complementary C1/C2
strengths or constraints that cannot safely be enforced by C1.

## Governance

Gate 6M remains valid under the old raw-NDCG protocol. Gate 6B remains valid as
projection and architecture evidence under that protocol. This document is a
new experiment-governance artifact; it does not retroactively rescore or
promote Gate 6B.
