# Gate 5-F3 Task Contract and Start Gate

**Work Object ID:** `armie-retrieval-v051-gate5-f3-confirmed-result-rendering`
**Project ID:** `armie-retrieval-platform`
**Core:** ARMIE Company OS Core v0.1
**State:** active local candidate; not Founder-accepted

## Objective

Resolve only F6: route confirmed interpretation execution into the canonical
Workbench response state, preserving the accepted Gate 5 interpretation and C1
execution boundary.

## Scope and exclusions

Allowed: the bounded Workbench/application integration, its focused tests,
browser evidence, and governance Result Package updates.

Excluded: interpretation semantics, C1 redesign, Dataset v1/v2, benchmark
changes, Gate 6, release work, commit, tag, push, and deployment changes.

## Authority and required context

- Founder-authorized Gate 5 scope and accepted Gate 3J/Gate 4 decisions.
- `company-os/PROJECT_STATE.md`, `company-os/CURRENT_WORK.md`, and
  `company-os/README.md`.
- [Gate 5-F3 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md).
- Existing C1 contracts, Workbench protocol, Dataset v2 identity, and live
  verification evidence.

## Evidence profile

The Result Package must include focused backend/API/frontend tests, the live
browser path, positive and valid zero-result behavior, provenance, scope
limits, and the candidate transition. No Gold/Silver quality claim is allowed.

## Stop condition and acceptance

Stop at `READY_FOR_FOUNDER_RETEST_3`. The Founder must retest confirmed
five-result and valid zero-result rendering before Gate 5 can be accepted.
Agents may not mark Gate 5-F3 or Gate 5 accepted and may not start Gate 6.

## Evidence-layer classification (as of 2026-08-17)

| Layer | Fact |
|---|---|
| Local-uncommitted | Gate 5-F3 code, tests, docs, and this contract are present in the dirty worktree. |
| Committed | Latest committed HEAD is v0.5.0 closeout `f181960`; no v0.5.1 commit exists. |
| Remote | `origin/main` is `f181960`; no v0.5.1 branch/tag is present. |
| GitHub Release object | No v0.5.1 Release object has been created or verified. |
| Founder acceptance | Gate 5-F3 retest and Gate 5 acceptance remain pending. |

## Completion write-back

Execution must produce a Result Package, verification record, candidate
transition, and this checklist. Only a received Founder decision authorizes
structured updates to accepted state in `PROJECT_STATE.md`, `DECISIONS.md`, and
`EVALUATIONS.md`.
