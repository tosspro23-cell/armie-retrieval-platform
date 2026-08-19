# ARMIE Retrieval Platform v0.5.0 Post-Release Architecture Review

**Work Object:** `armie-retrieval-v050-post-release-architecture-review`
**Status:** Review complete; proposed next scope is
`READY_FOR_FOUNDER_ACCEPTANCE`
**Date:** 2026-08-15

## Review verdict

**B — v0.5.1 direction valid but requires prerequisite debt work.**

`v0.5.1 — Governed Natural Language → RetrievalContract` is architecturally
continuous with v0.5.0: it adds an interpretation and confirmation layer before
the existing deterministic contract compiler and C1 runtime. It must remain a
bounded proposal until a founder-approved Gate 0. Stable index identity,
registry/provenance contract checks, and a dedicated extraction benchmark
charter are prerequisite closure items; none authorizes implementation here.

## 1. v0.5.0 final architecture outcome

- **C0:** H2 Dense, unconstrained/free semantic retrieval.
- **C1:** promoted path: H2 Dense plus deterministic native Elasticsearch
  pre-filter for approved structured hard constraints.
- **C2:** diagnostic/secondary candidate-pool post-filter only; it produced no
  material eligible-quality gain over C1 and added latency.
- **C3:** deferred; no evidence supports promotion.

The final decision is based on repaired Gate 6D evidence, not obsolete
intermediate Gate 6 conclusions. See
[`gate6d-benchmark-results.md`](gate6d-benchmark-results.md) and
[`v0.5.0-release-notes.md`](v0.5.0-release-notes.md).

## 2. What v0.5.0 proved

Released evidence supports these bounded claims:

- deterministic `RetrievalContract` validation and compilation;
- supported structured HARD constraints and explicit exclusions;
- strict no-relaxation behavior, including explicit unsupported states;
- UNKNOWN handling in the contract/evidence path;
- native Elasticsearch pre-filter correctness for the approved projection;
- projection parity for approved fields;
- constrained Top-K semantics and strict shortfall without ineligible backfill;
- improved eligible-conditioned utility over C0 under the frozen protocol;
- zero prohibited/violation intrusion in repaired C1 evaluation;
- reduced hard-negative intrusion under the eligible-conditioned objective;
- per-result constraint provenance and Workbench explanation;
- browser-level structured-query workflow and registry-backed controls;
- reproducible release identity, validation, and governance traceability.

The primary Gate 6D table reports C1 eligible NDCG@5 `0.4917`, eligible P@5
`0.4913`, eligible fill@5 `0.6108`, satisfaction@5 `0.8261`, violation `0`,
and prohibited `0`; C0 eligible NDCG@5 was `0.3027` with violation `0.6130`.
These are controlled synthetic benchmark results, not production quality claims.

## 3. What v0.5.0 did not prove

| Capability | Boundary |
|---|---|
| Arbitrary natural-language → contract extraction | NOT IN SCOPE |
| Automatic HARD/SOFT interpretation | UNPROVEN |
| Implicit constraint inference | UNPROVEN |
| General temporal semantics | DEFERRED |
| Relationship semantics | DEFERRED |
| Delivery/evidence qualification | DEFERRED |
| Graph retrieval or evidence-dependent post-verification | DEFERRED |
| Production C2 or C3 | DEFERRED |
| ANN optimization | NOT IN SCOPE |
| Large-scale production traffic behavior | UNPROVEN |
| Natural expert-corpus quality | KNOWN LIMITATION; Dataset v2 is synthetic |

These are boundaries, not failures of the released scope.

## 4. Evaluation and governance lessons

The Gate 6 sequence established durable rules:

1. Evaluation infrastructure is part of product architecture.
2. Benchmark validity must be separated from model/runtime quality.
3. Projection and index truth require independent audits.
4. Raw semantic relevance is insufficient when eligibility is a hard product
   objective.
5. Promotion rules must optimize the declared eligible-conditioned objective.
6. Invalid or inconclusive experiments remain governance history and must not be
   erased or silently treated as architecture evidence.

The repaired sequence covered benchmark semantic alignment, exclusion
serialization, prohibited-violation evaluation, projection mismatch and repair,
failure decomposition, and the transition from raw to eligible-conditioned
metrics.

## 5. Productization lessons

Gate 7–7F makes these permanent product rules:

- validate against the founder/user environment, not only isolated ports;
- distinguish candidate pool from returned product results;
- expose structured facts that justify constraint satisfaction;
- retain controlled-vocabulary categorical controls and explicit edit surfaces;
- label strategy and scores according to actual runtime behavior;
- prevent stale C0/C1 session state from leaking across queries;
- show unsupported, strict-shortfall, and provenance states explicitly;
- preserve free-query semantic retrieval as a separate C0 path.

## 6. Company OS and release governance lessons

The release demonstrated that technical completion and governance completion
are different states. Permanent policy now requires an active Work Object,
Result Package, verification, founder acceptance where required, and structured
write-back. Release identity is immutable (`v0.5.0` tag and target), while
`main` is mutable (`f181960`). Post-push reconciliation must record both, plus
GitHub Release-object status. Repository-level `AGENTS.md` now enforces this
preflight and completion sequence.

## 7. Technical debt inventory

| Item | Classification | Review position |
|---|---|---|
| Stable index alias for the temporary Gate 6B dense identity | MUST FIX BEFORE v0.5.1 release; can be bounded infrastructure work before Gate 0 close | Prevents ambiguous reproducibility |
| Limited populated industry coverage and no Healthcare positive example | CAN FIX DURING v0.5.1 evaluation preparation | Keep synthetic limitations explicit |
| Legacy hardcoded-port test configuration | NON-BLOCKING | Founder-environment validation resolved the material release issue |
| Registry identity/versioning | CAN FIX DURING v0.5.1 Gate 0 | Freeze compatibility and capability metadata before extraction |
| Provenance schema stability | CAN FIX DURING v0.5.1 Gate 0 | Preserve candidate-contract and execution provenance separately |
| Workbench UX | NON-BLOCKING | Remaining work is bounded clarity, not architecture |

## 8. Proposed v0.5.1 boundary

The problem is intentionally narrow:

> Users currently populate structured filters manually. v0.5.1 would allow a
> user to express supported constraints in natural language and produce a
> candidate `RetrievalContract`.

The proposed pipeline is:

```text
Natural-language request
        ↓
Constraint interpretation/decomposition
        ↓
Candidate RetrievalContract
        ↓
Deterministic validation/compiler
        ↓
User-visible interpretation
        ↓
Confirm/edit
        ↓
Existing C1 execution
        ↓
Results + constraint evidence
```

This is a patch-level interface/interpretation layer, not a retrieval-runtime
architecture change. It becomes v0.6-level only if it expands into temporal,
relationship, graph/evidence retrieval, or a new runtime execution model.

## 9. HARD/SOFT interpretation policy

Explicit mandatory language such as `must`, `at least`, `no less than`,
`exclude`, `only`, and `require` may produce candidate HARD constraints.
Preference language such as `prefer`, `ideally`, and `nice to have` must not
silently become HARD. Ambiguous language becomes unresolved/suggested and
requires confirmation. Semantic intent remains separate from constraints.

Example: Azure expertise is semantic intent; Healthcare, `>=20` years,
Senior, and an explicit Financial Services exclusion are candidate constraints
only when the text supports those meanings.

## 10. Confirmation boundary

The initial v0.5.1 design should require user confirmation/edit before executing
any extracted HARD constraint. False HARD constraints can exclude valid
profiles, so the system must prefer safe under-constraint plus visible review
over silent over-constraint. Existing structured controls remain the edit,
correction, and explicit fallback surface.

## 11. Extraction failure semantics

The candidate contract must not silently omit unsupported meaning. The system
should return explicit states for unsupported fields/operators, ambiguous
polarity or values, unknown categorical values, mixed supported/unsupported
requests, no extractable constraint, contradictory constraints, and unsupported
temporal/relationship language. No unchecked model output reaches runtime.

## 12. Proposed extraction evaluation

Natural-language interpretation must be evaluated separately from retrieval
ranking. Proposed metrics are field extraction precision/recall, operator
accuracy, normalized-value accuracy, exclusion/polarity accuracy, HARD/SOFT
classification accuracy, unsupported-detection precision/recall, exact
contract match, partial contract match, false-hard-constraint rate, and
missed-hard-constraint rate.

The primary safety metric should be **False Hard Constraint Rate**. Its risk is
greater than missed-constraint risk because it can remove valid candidates
before Dense ranking. Numerical promotion thresholds are intentionally not
fixed by this review.

## 13. Benchmark concept

Before generation, a benchmark charter should cover explicit numeric minimums,
ranges, industry, role, seniority, location, exclusions, conjunctions,
preference versus requirement, ambiguity, unsupported temporal/relationship
language, contradictions, mixed supported/unsupported requests, and semantic
queries with no hard constraint. Each item needs natural text, semantic intent,
expected candidate contract, support/ambiguity labels, and rationale.

## 14. Extraction strategy comparison

| Strategy | Strengths | Risks |
|---|---|---|
| Deterministic rules | precision, determinism, transparency | limited recall and language coverage |
| LLM structured extraction | broader paraphrase coverage | false HARD risk, cost, nondeterminism |
| Hybrid rules + LLM | balances coverage and control | orchestration/evaluation complexity |
| Constrained structured-output model | schema discipline and observability | still requires semantic validation and model operations |

The recommended Gate 0 hypothesis is a conservative hybrid: deterministic
recognition for explicit supported patterns, model assistance only for bounded
candidate interpretation, and the deterministic compiler as final authority.

## 15. Explicit v0.5.1 non-goals

Exclude temporal reasoning, relationship graphs, delivered-for evidence,
hands-on delivery verification, graph retrieval, C2/C3 promotion, ANN tuning,
and unrelated inference infrastructure. These remain v0.6+ candidates or
deferred work.

## 16. Recommended Gate sequence

1. **Gate 0:** charter and contract-interpretation semantics.
2. **Gate 1:** extraction schema and benchmark design.
3. **Gate 2:** baseline deterministic/hybrid extraction implementations.
4. **Gate 3:** extraction evaluation and false-hard analysis.
5. **Gate 4:** confirmation/edit UX.
6. **Gate 5:** NL → candidate contract → C1 integration.
7. **Gate 6:** founder acceptance and release readiness.

This sequence keeps evaluation and safety ahead of runtime promotion.

## 17. Review disposition

The proposed v0.5.1 scope is **recommended but requires prerequisite debt work**.
It is not accepted or active. The next action is founder review of this Result
Package and explicit authorization of a Gate 0 Work Object. No v0.5.1 code or
benchmark has been started by this review.

## Evidence boundary

Primary evidence: [`v0.5.0 release notes`](v0.5.0-release-notes.md),
[`Gate 6D results`](gate6d-benchmark-results.md),
[`Gate 6D protocol`](gate6d-evaluation-protocol.md),
[`Gate 7D acceptance`](gate7d-manual-acceptance.md),
[`Gate 8 readiness`](gate8-release-readiness.md), and the
[`post-release closeout`](post-release-closeout.md). Dataset v2 remains a
controlled synthetic relevance benchmark and does not establish real-world
expert-search quality.
