# ARMIE Retrieval Platform Agent Policy

This file is the repository-level execution policy for Codex and other agents.
The authoritative governed project state and detailed protocol remain in
[`company-os/`](company-os/README.md).

## Company OS Core reference

**Project ID:** `armie-retrieval-platform`
**Core:** ARMIE Company OS Core v0.1 at
`/Users/ting/Documents/New project/armie-company-os-core/`
**Project Adapter:** [`company-os/PROJECT_ADAPTER.md`](company-os/PROJECT_ADAPTER.md)

The Core is a shared protocol reference, not a copied source tree or a second
source of project state. `company-os/PROJECT_STATE.md`, the active Work Object,
and local Result Packages remain authoritative for this project.

## When Company OS applies

Use the Company OS protocol for any state-changing task, including a new gate,
version, architecture or capability change, benchmark/evaluation promotion,
release, or material project-status change. Read-only explanations,
investigations, exploratory reviews, and debugging with no accepted state
change do not require unnecessary Company OS mutations. If exploration produces
an accepted decision, it becomes state-changing work.

## Mandatory Start Gate

Before state-changing execution:

1. Read the Core protocol entry guidance, `company-os/PROJECT_STATE.md`, and
   `company-os/CURRENT_WORK.md`.
2. Resolve an active Work Object ID and Task Contract, plus its State
   Package/reference.
3. Verify its objective, scope, acceptance criteria, execution boundaries, and
   stop condition.
4. Check whether Company OS is synchronized or `STALE / OUT-OF-SYNC` with
   verified repository and remote facts.
5. Confirm the dispatch names the Project ID, Core reference, active Work
   Object, Task Contract, allowed paths/systems, evidence profile, acceptance
   authority, and expected Result Package.

If the Work Object or required state package is missing, or the records are
stale, do not begin normal execution. Reconcile the state or create/activate
the Work Object first. Do not rely on conversational context alone.

There must be exactly one active Work Object in `company-os/CURRENT_WORK.md`.
Earlier objects must be marked `Archived` or `Superseded`; a historical entry
must not retain an active heading or state. Every material dispatch must name
the Task Contract/Start Gate artifact and classify claims as local-uncommitted,
committed, remote, GitHub Release object, or Founder acceptance. Run
`python3 scripts/check_company_os_consistency.py` before Founder review or
release review; a failed check is a stop condition.

## Execution and completion

Stay within the active Work Object. Completion is:

`execution → Result Package → verification → acceptance status → Company OS write-back`

Code complete or tests passing is not governance-complete until the verified
state is written back to the semantically affected Company OS records. Record
objective facts automatically where appropriate; record
`READY_FOR_FOUNDER_ACCEPTANCE` or `PENDING` for founder-gated decisions.

Agents must not independently mark architecture promotion, release acceptance,
material scope changes, version freezes, or roadmap decisions `ACCEPTED` unless
the founder explicitly accepted them in the current context or an authoritative
Company OS record already documents that acceptance.

## Release reconciliation

Release work requires a release Work Object and pre/post-push reconciliation.
After all intended pushes, record separately:

- immutable release identity: version, tag name, annotated tag object, tag
  target, and applicable benchmark/protocol/release fingerprints;
- mutable repository state: local branch HEAD, remote branch HEAD, worktree,
  active Work Object, and GitHub Release-object status.

Never substitute the latest branch commit for the release tag target. If a
closeout commit advances `main`, record both values. A release is not
governance-complete until final remote state and Company OS write-back are
verified.

## State drift and source of truth

Use this operational hierarchy:

1. verified repository, Git, and remote facts;
2. Company OS current state records;
3. active Work Object and Result Package;
4. task-specific user instructions;
5. historical documentation.

Historical gate documents are evidence, not necessarily current state. If facts
and Company OS differ, report `STALE / OUT-OF-SYNC` and reconcile before
continuing governed execution. This policy does not authorize autonomous scope
expansion: finishing one version or gate never starts the next.

## Bounded automatic write-back

Agents may write verified execution results, validation results, Git facts,
release references, Result Package data, and Work Object execution status.
They must not silently decide founder acceptance, architecture promotion,
version scope, product strategy, or future roadmap direction.

## Example

For “run v0.5.1 Gate 1”: read Company OS; resolve or create the active Work
Object and contract; execute only its bounded scope; produce and verify the
Result Package; mark `READY_FOR_FOUNDER_ACCEPTANCE` when required; write verified
state back; then stop at the Work Object’s stop condition.

## Non-goals

This policy does not create a background governance runtime, authorize the next
gate/version, redesign Company OS, or replace project-specific technical
instructions. Nested instruction files, if added later, apply only to their
subtree and must not contradict this repository policy or `company-os/` state.
