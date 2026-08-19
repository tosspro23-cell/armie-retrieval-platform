# Gate 3G — Prospective Staged Interpretation Promotion Results

**Status:** Candidate-complete; **EVIDENCE INVALID — benchmark quality defect**
**Candidate:** `deterministic-staged-v2-gate3fr`
**Benchmark:** `v0.5.1-staged-interpretation-promotion-v1`
**Run count:** one execution only; invalidated, not rerun.

## Execution identity

The benchmark was frozen before execution at 180 items with SHA-256
`a9c55a271054049af6238eac868c14a43a279105532b34ed32a0bc41963c9d6f`.
The evaluator was `scripts/run_v051_gate3g.py`; the candidate was executed
exactly once. The historical 120-item benchmark was not used.

## Quality audit and invalidation

Post-run quality audit found only **58 unique normalized requests out of 180**
(122 duplicate rows). The six role strata are numerically balanced at 30 each,
but the repeated language is template inflation rather than meaningful
linguistic diversity. This violates the Gate 3G requirement to avoid trivially
recognizable, lightly repeated benchmark language. The run is therefore
invalid evidence and must not support promotion.

Because the defect was discovered after candidate results were visible, the
benchmark is not edited and the result is not silently rerun. A future repair
requires a new benchmark identity and explicit rerun authorization.

## Observed run (diagnostic only)

The deterministic arm completed 180/180 with apparent metrics of 100% role
accuracy, zero False REQUIRED/EXCLUDED/final False HARD, 100% mapping,
normalization, unsupported preservation, and exact match. Latency mean/p50/p95
was 0.084/0.067/0.107 ms. These values are reported for traceability only and
are not promotion evidence because the benchmark is invalid.

First-failing-stage distribution was `none: 180`; this is consistent with the
overly regular authored language and reinforces the invalidation rather than
demonstrating generalization.

## Decision

**C — EVIDENCE INVALID.** No staged architecture promotion is made. Gate 4
remains inactive. The next action is to obtain authorization for a new,
linguistically diverse benchmark family, then freeze and run it exactly once.
