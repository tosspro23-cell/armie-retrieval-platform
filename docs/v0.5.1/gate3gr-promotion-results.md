# Gate 3G-R Prospective Benchmark Results

**Verdict:** Candidate evidence is valid, but the candidate is **not promoted**.
The frozen prospective benchmark passed its admission gates; the deterministic
candidate failed the frozen quality/safety thresholds. Gate 4 remains inactive.

## Pre-execution identity and audit

| Field | Value |
|---|---|
| Benchmark | `v0.5.1-staged-interpretation-promotion-v2` |
| Rows | 160 (25 per six single-role strata + 10 mixed) |
| Fixture SHA-256 | `7052b8c514778a95d54fc1f2bfaf938cf52e29c22f57b3f0440e1b6fa4c35220` |
| Exact normalized duplicates | 0 |
| Near-duplicate pairs (Jaccard >= .85) | 0 |
| Pattern families | 33; largest family 10.63% |
| Mixed/compositional rows | 10/160 |
| Candidate | `deterministic-staged-v2-gate3fr` |

The benchmark was audited before the one candidate execution. Its controlled
synthetic language is prospective validation material, not real-world quality.

## Single execution metrics

| Metric | Result | Frozen threshold |
|---|---:|---:|
| Coverage | 100% | 100% |
| Overall role accuracy | 38.75% | >=85% |
| False REQUIRED | 1.25% | 0% |
| False EXCLUDED | 0% | 0% |
| Final False HARD | 1.25% | 0% |
| Mapping accuracy | 71.88% | >=95% |
| Operator/value accuracy | 71.88% | >=95% |
| Exact CandidateInterpretation | 33.75% | >=80% |
| Supported precision | 100% | >=95% |
| Supported recall | 60% | >=80% |
| Unsupported preservation | 36% | >=95% |

Per-stratum role accuracy: REQUIRED 40%, EXCLUDED 20%, PREFERRED 24%,
CONTEXT_ONLY 80%, UNSUPPORTED 36%, AMBIGUOUS 20%, MIXED 70%.

## Failure decomposition and generalization

First failure counts were stage 2 role: 98 rows, stage 3 mapping: 8 rows, and
no failure: 54 rows. Compared with the 36-case development validation
(86.49% role accuracy, 100% safety rates, 85.71% preferred), this is a large
prospective generalization gap: role accuracy -47.74 percentage points and
preferred accuracy -61.71 points. The gap is evidence about this candidate and
benchmark, not a claim about production traffic.

## Decision

**Decision B — no promotion.** The benchmark is valid evidence, but the frozen
candidate fails safety and quality thresholds. Do not tune the candidate or
rerun within Gate 3G-R; propose a new authorized gate if the Founder wants
further diagnosis. No evidence warrants C1/C2 or Gate 4 work here.

Machine-readable execution evidence is retained at
`.artifacts/v051_gate3gr_results.json` (ignored local artifact).
