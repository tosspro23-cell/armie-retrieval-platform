# ARMIE Retrieval Platform — Company OS Project State

**Protocol:** ARMIE Company OS v0.1  
**State basis:** verified Git/remote facts, current local governance records,
Result Packages, and explicit Founder decisions. Local-uncommitted evidence is
never treated as committed or released.
**Last verified:** 2026-08-30

## Objective

Build and validate a production-oriented retrieval platform while preserving
explicit architecture contracts, evidence-led evaluation, and reproducible
dataset boundaries.

## Authoritative current state

**Active Work Object:** none. `GOV-CONV-001` is Founder-accepted and closed as
the latest governance-interface alignment Work Object. It is a governance-only
adoption record; no product, CI, release, or version transition follows from
it. Earlier closed Work Objects remain preserved as archived records in
`CURRENT_WORK.md`.

GOV-CONV-001 adds a source-pointed Governance Surface and common Core mapping
without changing product behavior, release state, version scope, or CI
workflow. The Founder accepted the Result Package on 2026-08-30. Its Start
Gate and Result Package are
`GOVERNANCE_CONVERGENCE_PHASE1_START_GATE.md` and
`GOVERNANCE_CONVERGENCE_PHASE1_RESULT_PACKAGE.md`.
Its accepted governance files are committed at
`718392c50bcb07deb56aa7bcc7374318bfa3f2a1` and fast-forwarded into verified
`origin/main`; Retrieval is the current `DIRECT` reference sample for the
common governance interface.

`ci-revival-2026-08` (closed 2026-08-26) restored a passing GitHub Actions
CI baseline on `main` using only test-harness and CI-configuration changes —
no change to `src/armie_retrieval/`, `services/`, or any retrieval/planning/
ranking/C1 behavior. It fixed four independently-verified CI root causes
plus two narrowly-scoped follow-ups surfaced by the 3.9 matrix leg and by
Codex's automated PR review. Full detail, evidence, and the Founder
authorization for this write-back and merge are in `CURRENT_WORK.md`.

The Founder accepted Gate 5, including the bounded F/F2/F3 fixes, froze the
v0.5.1 capability boundary, and authorized stabilization, GitHub publication,
and closeout. v0.5.1 is released. The capability remains: governed
natural-language interpretation → clarification when necessary → explicit user
resolution → confirmation → canonical `RetrievalContract` → existing
deterministic C1 with provenance. No v0.6 work is authorized.

**Verified release facts:** commit
`c4bf57fd4ead76cdc18a36e885eea9a5215401a4` was pushed on `main` and remains
reachable from `origin/main`;
annotated tag `v0.5.1` has tag object
`6ef90af0b76add2186cd31ef0d74150665234bf8` and peels to that commit; the
published GitHub Release object is
[`v0.5.1`](https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1).

The latest closed governance Task Contract/Start Gate is
[`GOVERNANCE_CONVERGENCE_PHASE1_START_GATE.md`](GOVERNANCE_CONVERGENCE_PHASE1_START_GATE.md).
The earlier closed release contract remains
[`V051_RELEASE_START_GATE.md`](V051_RELEASE_START_GATE.md). The 2026-08-17 governance audit and remediation record is
[`GOVERNANCE_AUDIT_2026-08-17.md`](GOVERNANCE_AUDIT_2026-08-17.md).

- v0.4.0 Gate 5 relevance benchmark is completed and committed at the
  existing repository baseline; this is distinct from the active v0.5.1 Gate 5
  candidate.
- Dataset v1 is immutable and remains the controlled synthetic regression
  baseline.
- Gate 5.5A was founder-accepted and committed in `57a1be9`.
- Gate 5.5B completed the full v2 benchmark and stability checkpoint; benchmark
  documentation is committed in `9973367` and the dense-index resumability
  checkpoint is `58baad4`. Its controlled synthetic results must not be treated
  as external or real-world expert-search validation.
- Gate 6 Workbench Acceptance / Relevance Experiment UX was founder-accepted
  and committed at `5ee33a1b098c20a313fe04603e371e2fc4768ee6`. It preserves
  existing runtime/planner/retriever semantics and has backend endpoint checks
  plus 17 Chromium browser acceptance checks after final UI polish.
- Gate 7 release preparation was founder-accepted and completed. Release
  commit `266bf5b8c4a81aee30231d486312b03c4eca96db` is on `main`, and annotated
  tag `v0.4.0` points to that commit and is present on `origin`.
- GitHub contains the pushed branch and tag. The GitHub Releases API returned
  404 for `v0.4.0`, so a GitHub Release object was not created; the published
  Git tag is the release reference.
- v0.5.0 engineering and Git release is founder-accepted and closed. The
  release sequence is represented by commits `5425b2e`, `a42789d`, `0102cdb`,
  and `05e661f`; follow-up closeout documentation is `f181960`.
- Annotated tag `v0.5.0` has tag object `b4230aee` and target `05e661f`.
  The release identity is immutable and must not be moved.
- The final local and remote branch head is `f181960`. This is mutable branch
  state and is distinct from the release tag target.
- The Git tag is present remotely. No GitHub Release object was created or
  independently verified.
- v0.5.1 Gate 0 and Gate 1 were accepted. Gate 2 was accepted by the founder
  as an experimental result with Outcome E (insufficient evidence), and Gate 3
  was explicitly authorized. Gate 3C completed auditable model/hybrid coverage
  and was founder-accepted with architecture decision D (no promotion). Gate
  3D and its subsequent architecture review are founder-accepted with no
  extractor promotion. Gate 4 Workbench clarification/confirmation is
  founder-accepted. Gate 5-F3 is the active candidate and supersedes F2;
  no Gate 5 acceptance, Gate 6 authorization, or production/release promotion
  has started.

## Gate map

| Gate | State | Evidence |
|---|---|---|
| Gate 5 | Completed and committed | `docs/v0.4.0/gate5-results.md`, `docs/v0.4.0/validation-report.md` |
| Gate 5.5A | Completed, founder-accepted, committed | `57a1be9`, `docs/v0.4.0/dataset-v2-pilot-audit.md` |
| Gate 5.5B | Completed and benchmark checkpoint committed | `58baad4`, `9973367`, `docs/v0.4.0/gate55b-results.md` |
| Gate 6 / Query Lab | Completed, founder-accepted, committed | `5ee33a1`, `apps/workbench/tests/gate6.acceptance.spec.ts`, `docs/v0.4.0/validation-report.md` |
| Gate 7 / release | Completed, founder-accepted, pushed | `266bf5b`, annotated `v0.4.0`, remote refs, `docs/v0.4.0/release-notes.md` |
| v0.5.0 Gate 1.5–8 | Completed within the accepted release scope | `docs/v0.5.0/gate8-release-readiness.md`, `docs/v0.5.0/v0.5.0-release-manifest.json` |
| v0.5.0 Gate 9 / release | Completed, founder-accepted, pushed | `company-os/CURRENT_WORK.md`, `docs/v0.5.0/post-release-closeout.md`, tag `v0.5.0` |
| v0.5.0 post-release review | Review complete; v0.5.1 scope subsequently authorized through P0/Gate 0 | `docs/v0.5.0/post-release-architecture-review.md`, `company-os/POST_RELEASE_REVIEW.md` |
| v0.5.1 P0 | Accepted with carry-forward conditions | `docs/v0.5.1/p0-runtime-contract-stabilization.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 0 | Completed, founder-accepted | `docs/v0.5.1/gate0-nl-contract-charter.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 1 | Completed, founder-accepted | `docs/v0.5.1/gate1-interpretation-benchmark-design.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 2 | Completed, founder-accepted as experimental Outcome E | `docs/v0.5.1/gate2-extraction-baseline-comparison.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 3 / 3C | Evidence accepted; architecture D (no promotion) | `docs/v0.5.1/gate3c-resumable-evaluation.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 3D | Completed and founder-accepted; architecture D (no promotion) | `docs/v0.5.1/gate3d-semantics-refinement.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 3E | Completed, founder-accepted; staged architecture Path A selected | `docs/v0.5.1/gate3e-architecture-reassessment.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 3F | Completed and founder-accepted as development evidence; promising, not promoted | `docs/v0.5.1/gate3f-staged-interpretation-development.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 3F-R | Completed and founder-accepted; deterministic staged candidate remains unpromoted | `docs/v0.5.1/gate3fr-stage2-refinement.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 3G | Candidate-complete; evidence invalid due benchmark duplication; no promotion | `docs/v0.5.1/gate3g-promotion-results.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 3G-R | Completed and founder-accepted; Decision B, no promotion | `docs/v0.5.1/gate3gr-promotion-results.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 3H | Completed and founder-accepted; Decision C, no model candidate | `docs/v0.5.1/gate3h-model-capability-results.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 3I | Completed and founder-accepted; Decision B, no promotion | `docs/v0.5.1/gate3i-role-only-results.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 3J | Completed, founder-accepted; clarification protocol v1 | `docs/v0.5.1/gate3j-clarification-protocol.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 4 | Completed, founder-accepted; bounded Workbench clarification/confirmation UX | `docs/v0.5.1/gate4-clarification-confirmation-workbench.md`, `company-os/DECISIONS.md` |
| v0.5.1 Gate 5-F | Candidate-complete; superseded by F2 | `docs/v0.5.1/gate5-confirmed-c1-e2e.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 5-F2 | Founder-verified F4/F5; superseded by F3 | `docs/v0.5.1/gate5-confirmed-c1-e2e.md`, `company-os/CURRENT_WORK.md` |
| v0.5.1 Gate 5-F3 | Closed as part of Founder-accepted Gate 5 | `docs/v0.5.1/gate5-confirmed-c1-e2e.md`, `company-os/CURRENT_WORK.md`, `tests/test_v051_gate4_workbench.py`, `apps/workbench/tests/gate7c.integration.spec.ts` |
| v0.5.1 release / closeout | Released, Founder-authorized, closed | `c4bf57f`, annotated `v0.5.1`, [GitHub Release](https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1), `company-os/CURRENT_WORK.md` |
| `ci-revival-2026-08` | Completed, Founder-authorized write-back and merge | [PR #1](https://github.com/tosspro23-cell/armie-retrieval-platform/pull/1), commits `02a816a`/`05a6f8e`/`edb80ee`, `company-os/CURRENT_WORK.md` |
| `GOV-CONV-001` | Founder-accepted governance-interface alignment; no executable capability claim | `company-os/GOVERNANCE_SURFACE.md`, `company-os/GOVERNANCE_CONVERGENCE_PHASE1_RESULT_PACKAGE.md`, `company-os/DECISIONS.md` D-037 |

## Constraints and accepted boundaries

- Preserve Architecture Freeze decisions and existing runtime behavior.
- Preserve Dataset v1 and Dataset v2 implementation exactly as currently
  reviewed; this Company OS baseline adds protocol documentation only.
- Do not infer founder acceptance from an agent result; the release state below
  is recorded because the founder explicitly accepted the release.
- Do not begin a subsequent release or version without a new founder decision.
- v0.5.0 is an accepted release state.
- v0.5.1 Gate 0, Gate 1, and Gate 2 experimental acceptance are completed and
  founder-authorized. Gate 3C is accepted with architecture decision D (no
  promotion); Gate 3D and Gate 3E are founder-accepted, and Gate 3F is
  accepted as development evidence. Gate 3F-R is authorized for one bounded
  Stage 2 refinement. Gate 3G was authorized and is evidence-invalid due
  benchmark duplication. Gate 3G-R completed one valid prospective run and was
  Founder-accepted with Decision B (no promotion). Gate 3H completed a bounded
  model capability study and was Founder-accepted with Decision C (no
  model-assisted candidate). Gate 3I then showed a real but insufficient role-only
  model lift; Decision B was Founder-accepted. Gate 3J clarification protocol
  v1 and Gate 4 Workbench UX were subsequently accepted. Gate 5 and its
  bounded confirmed-interpretation → existing C1 integration fixes are
  accepted. v0.5.1 is released and closed; v0.6 work remains inactive.
- Do not treat a Git tag as proof that a GitHub Release object exists.

## Known limitations and risks

- The v1 corpus contains 9,496 duplicate normalized summaries out of 10,000.
- Both benchmarks contain templated synthetic language and controlled-vocabulary
  leakage risk.
- Gold is an independent structured audit, not external human ground truth.
- Results must not be generalized to natural expert-network data.
- Gate 5.5A is a pilot quality gate, not a production-realism claim.

## Open questions

No active Work Object or release-open question remains. A future version or
executable task requires a new Work Object, accepted Task Contract, and
explicit Founder authorization.

## Next actions

1. Preserve v0.5.1 as the released state. Do not start v0.6 without a new
   Founder-authorized Start Gate.

## Source and provenance notes

Verified facts are drawn from repository history, current `git status`,
`git ls-remote` remote
references, the GitHub Releases API, Gate 5.5A/5.5B documents, tests, and the
clean release checkout. Founder-confirmed acceptance is recorded only because
the founder explicitly provided it. The GitHub Release object, tag, target,
remote branch, and release commit were independently verified; a tag remains
distinct from a GitHub Release object.
This file is an operational state record, not a replacement for the
repository’s technical specifications. If Git or remote state differs from
this record after a state-changing task, mark the Company OS state
`STALE / OUT-OF-SYNC` until reconciled.
