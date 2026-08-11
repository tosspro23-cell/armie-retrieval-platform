# ARMIE Retrieval Platform — Company OS Project State

**Protocol:** ARMIE Company OS v0.1  
**State basis:** repository history, current repository documents, and current uncommitted worktree
**Last verified:** 2026-08-11

## Objective

Build and validate a production-oriented retrieval platform while preserving
explicit architecture contracts, evidence-led evaluation, and reproducible
dataset boundaries.

## Authoritative current state

- Gate 5 is completed and committed at the existing repository baseline.
- Dataset v1 is immutable and remains the controlled synthetic regression
  baseline.
- Gate 5.5A was founder-accepted and committed in `57a1be9`.
- Gate 5.5B completed the full v2 benchmark and stability checkpoint; benchmark
  documentation is committed in `9973367` and the dense-index resumability
  checkpoint is `58baad4`. Its controlled synthetic results must not be treated
  as external or real-world expert-search validation.
- Gate 6 Workbench Acceptance / Relevance Experiment UX is candidate-complete
  and verified in the current uncommitted worktree. It preserves existing
  runtime/planner/retriever semantics and has backend endpoint checks plus ten
  browser acceptance checks.
- Gate 6 has not received founder acceptance or a commit. Gate 7, release
  preparation, tag, and push have not started.

## Gate map

| Gate | State | Evidence |
|---|---|---|
| Gate 5 | Completed and committed | `docs/v0.4.0/gate5-results.md`, `docs/v0.4.0/validation-report.md` |
| Gate 5.5A | Completed, founder-accepted, committed | `57a1be9`, `docs/v0.4.0/dataset-v2-pilot-audit.md` |
| Gate 5.5B | Completed and benchmark checkpoint committed | `58baad4`, `9973367`, `docs/v0.4.0/gate55b-results.md` |
| Gate 6 / Query Lab | Candidate-complete; founder decision required | current worktree, `CURRENT_WORK.md`, `docs/v0.4.0/validation-report.md` |
| Gate 7 / release | Pending; not started | no activation, release, tag, or push evidence |

## Constraints and accepted boundaries

- Preserve Architecture Freeze decisions and existing runtime behavior.
- Preserve Dataset v1 and Dataset v2 implementation exactly as currently
  reviewed; this Company OS baseline adds protocol documentation only.
- Do not infer founder acceptance from an agent result; Gate 6 remains
  candidate-complete until explicitly accepted.
- Do not start Gate 7 or release work without an explicit founder decision.
- Do not tag, push, or change release state as part of this baseline.

## Known limitations and risks

- The v1 corpus contains 9,496 duplicate normalized summaries out of 10,000.
- Both benchmarks contain templated synthetic language and controlled-vocabulary
  leakage risk.
- Gold is an independent structured audit, not external human ground truth.
- Results must not be generalized to natural expert-network data.
- Gate 5.5A is a pilot quality gate, not a production-realism claim.

## Open questions

1. Does the founder accept the Gate 6 Result Package and authorize its commit?
2. After Gate 6 acceptance, what exact scope and evidence threshold should Gate
   7/release preparation use?

## Next actions

1. Founder reviews the Gate 6 Result Package in `CURRENT_WORK.md` and accepts
   or rejects the candidate transition.
2. If accepted, complete the write-back checklist and commit Gate 6; do not
   infer acceptance from the current worktree.
3. If rejected, record the reason and keep Gate 6 in candidate-complete state.

## Source and provenance notes

Verified facts are drawn from repository history, Gate 5.5A/5.5B documents,
tests, and the current uncommitted Gate 6 worktree. Founder-confirmed facts are
labelled as accepted only where explicitly provided; candidate states are not
accepted state. This file is an operational state record, not a replacement
for the repository’s technical specifications.
