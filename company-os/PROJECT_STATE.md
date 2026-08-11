# ARMIE Retrieval Platform — Company OS Project State

**Protocol:** ARMIE Company OS v0.1  
**State basis:** current repository documents and current uncommitted worktree  
**Last verified:** 2026-08-11

## Objective

Build and validate a production-oriented retrieval platform while preserving
explicit architecture contracts, evidence-led evaluation, and reproducible
dataset boundaries.

## Authoritative current state

- Gate 5 is completed and committed at the existing repository baseline.
- Dataset v1 is immutable and remains the controlled synthetic regression
  baseline.
- Gate 5.5A is implemented in the current uncommitted worktree as a Dataset v2
  realism pilot and quality-audit package.
- Gate 5.5A pilot evidence: 750 profiles, 40 queries covering all ten query
  categories, 30,000 draft judgements, 1.47% normalized-summary duplicate rate,
  0 invalid temporal records, and 100% positive-judgement evidence coverage.
- Full H1–H4, Query Lab/Gate 6, Gate 7, release preparation, tag, push, and a
  Gate 5.5A commit have not been performed.

## Gate map

| Gate | State | Evidence |
|---|---|---|
| Gate 5 | Completed and committed | `docs/v0.4.0/gate5-results.md`, `docs/v0.4.0/validation-report.md` |
| Gate 5.5A | Completed pilot; awaiting founder decision | `docs/v0.4.0/dataset-v2-pilot-audit.md`, current worktree, `CURRENT_WORK.md` |
| Gate 5.5B | Proposed, not active | Full Dataset v2 plus stability benchmark and v1/v2 comparison |
| Gate 6 / Query Lab | Pending and out of scope | No activation evidence |
| Gate 7 / release | Pending and out of scope | No activation evidence |

## Constraints and accepted boundaries

- Preserve Architecture Freeze decisions and existing runtime behavior.
- Preserve Dataset v1 and Dataset v2 implementation exactly as currently
  reviewed; this Company OS baseline adds protocol documentation only.
- Do not infer founder acceptance from an agent result.
- Do not start Gate 5.5B without explicit founder authorization.
- Do not tag, push, or change release state as part of this baseline.

## Known limitations and risks

- The v1 corpus contains 9,496 duplicate normalized summaries out of 10,000.
- Both benchmarks contain templated synthetic language and controlled-vocabulary
  leakage risk.
- Gold is an independent structured audit, not external human ground truth.
- Results must not be generalized to natural expert-network data.
- Gate 5.5A is a pilot quality gate, not a production-realism claim.

## Open questions

1. Does the founder accept the Gate 5.5A result and authorize Gate 5.5B?
2. If accepted, what exact scope and evidence threshold should Gate 5.5B use?

## Next actions

1. Founder reviews `CURRENT_WORK.md` and accepts or rejects the candidate
   transition.
2. If accepted, create a new activated Work Object for Gate 5.5B before any
   implementation or benchmark execution.
3. If rejected, record the reason and keep the project at the Gate 5.5A
   completed-pilot state.

## Source and provenance notes

Verified facts are drawn from the repository’s Gate 5 documents, Dataset v2
design/audit artifacts, tests, and the current uncommitted worktree. Proposed
states are labelled as proposed or pending. This file is an operational state
record, not a replacement for the repository’s technical specifications.
