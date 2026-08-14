# Gate 6A — Architecture Diagnosis

**Decision:** **D — Mixed: metric-objective mismatch and actual eligible
retrieval weakness are both material.**

## Findings

1. C1 correctly removes 94 relevant-but-ineligible C0 Top-5 candidates and
   eliminates explicit prohibited violations in the Gate 6M audit.
2. Raw NDCG therefore contains a legitimate objective mismatch: it rewards
   some candidates that the constraint contract requires removing.
3. The mismatch is not the whole explanation. Eligible-conditioned NDCG falls
   from 0.4161 (C0) to 0.2621 (C1), and Eligible Fill@5 falls from 0.3730 to
   0.2703.
4. The frozen C1 path falsely excludes relevant eligible candidates when it
   compiles predicates against `years_experience` and `seniority_rank`, which
   are absent from the inspected dense-index mapping. This is a projection
   mismatch, not an ANN hypothesis.
5. For existing categorical fields, 33 relevant eligible candidates pass the
   native filter but are absent from C1 Top-5, showing a separate filtered
   Dense ranking/retrieval weakness.
6. C2-50/C2-100 recover one relevant eligible candidate beyond C1 in the
   existing Gate 6M artifacts, improving that query's fill but not aggregate
   performance enough to satisfy frozen promotion rules.

## Promotion status

Gate 6M's decision remains unchanged: C1 is not promoted because NDCG@5 falls
from 0.7256 to 0.2191, exceeding the frozen 5pp degradation guardrail. C2 is
not promoted or reopened by this diagnostic.

## Recommended next gate

**Recommendation 3 — Fix the C1 filter/compiler/projection correctness defect
before any re-evaluation.**

The missing projection fields must be resolved through an explicitly approved
future change. Only after that correction should a new controlled experiment
separate residual filtered-ANN/ranking effects from projection correctness.
This recommendation is not executed in Gate 6A.

## Explicit non-conclusions

- No claim is made that C1's remaining ranking loss is solely Elasticsearch ANN
  behavior.
- No Gate 6M metric, threshold, benchmark fingerprint, or runtime behavior is
  changed retroactively.
- No C3 implementation or Gate 7 work is authorized.
- No formal re-evaluation is warranted until the projection mismatch is fixed
  and a new experiment is pre-registered.
