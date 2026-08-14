# Gate 6M — Metric Calculator Repair Review

**Status:** Repair validated; 230-run controlled re-execution complete

## Repair

The prior evaluator computed `Prohibited Constraint Violation@5` using
`candidate.eligible == false`. That incorrectly classified required numeric,
role, location or seniority failures as prohibited violations.

The repaired evaluator sets the flag only when the query has explicit
exclusions and the candidate has an exclusion-specific `VIOLATED` state. Generic
ineligibility, hard-negative identity, relevance grade and required-constraint
failure never imply prohibited violation. Queries without exclusions are
query-level `not_applicable` and are excluded from the applicable aggregate.

## Locked identity preserved

- Benchmark: `v0.5-constraint-extension-v1.1`
- Fingerprint: `6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb`
- Queries / Gold / Silver: 46 / 46 / 0
- Judgements: 460,000
- Dataset checksum unchanged

## Deterministic invariants

Nine Gate 6M invariants pass: required-only failure is not prohibited,
explicit exclusion violation is prohibited, mixed required/exclusion cases are
classified by exclusion state, multiple-exclusion semantics are correct,
no-exclusion queries are not applicable, UNKNOWN is not prohibited, and hard
negative status does not imply prohibited violation.

## Validation

- Gate 6M evaluator tests: 9 passed
- Gate 5C semantic tests: 6 passed
- Benchmark identity and asset immutability checks: passed
- Fingerprint unchanged: passed
- No benchmark or runtime asset was regenerated
