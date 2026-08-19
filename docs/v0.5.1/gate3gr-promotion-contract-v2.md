# Gate 3G-R Prospective Promotion Contract v2

**Status:** Frozen before candidate execution
**Benchmark:** `v0.5.1-staged-interpretation-promotion-v2`
**Candidate:** `deterministic-staged-v2-gate3fr`
**Registry:** `v0.5-c1-capability-registry-1`

This is a single-run prospective promotion experiment. It is not production
evidence, Gate 4 authorization, or autonomous promotion.

## Benchmark admission gates

- 160 held-out rows with 0 exact normalized duplicates.
- Deterministic token-Jaccard near-duplicate flag threshold: >=0.85; 0 flagged
  pairs.
- At least 20 narrative pattern families; largest family share <=20%.
- Six single-role strata contain 25 rows each, plus 10 compositional rows.
- All structured required/excluded spans carry field, operator, and value truth.
- Benchmark identity and SHA-256 are recorded before execution.

## Candidate thresholds

- Terminal coverage: 100%.
- False REQUIRED, False EXCLUDED, and final False HARD: 0%.
- Overall role accuracy: >=85%; each single-role stratum: >=80%.
- Registry mapping and operator/value accuracy: >=95% where expected.
- Exact CandidateInterpretation match: >=80%.
- Supported precision >=95%; supported recall >=80%; unsupported preservation >=95%.

Any benchmark or contract change requires a new authorized run.
