# ARMIE Company OS v0.1

ARMIE Company OS v0.1 is a manual, state-governed operating protocol. It is
not a Python runtime or UI. Versioned local project files are the authoritative
operational state; chats are for reasoning and Git remains the source of code
truth.

`AGENTS.md` is the repository-level execution policy for Codex/agents;
`company-os/` contains the current governed state and detailed protocol.

**Project ID:** `armie-retrieval-platform`<br>
**Company OS Core reference:** `/Users/ting/Documents/New project/armie-company-os-core/`<br>
**Project Adapter:** [PROJECT_ADAPTER.md](PROJECT_ADAPTER.md)

The Core supplies shared vocabulary and handoff semantics. These local
`company-os/` records remain the authoritative project state, decisions,
evidence index, and Work Object history; the Core is not copied into this
repository and does not introduce a second Git or release history.

## Operating contract

1. Read the current state.
2. Create or activate a Work Object.
3. Define the task contract.
4. Execute within scope.
5. Produce a Result Package with evidence and scope limits.
6. Verify the result independently where practical.
7. Propose a candidate state transition.
8. The founder accepts or rejects it.
9. Complete the structured write-back checklist.

Agents may propose changes and produce evidence. Agents do not directly change
accepted authoritative state, mark work accepted, or treat a result as founder
authorization. Consequential decisions remain with the founder.

## Project-level Start Gate

Before an agent starts a new version, gate, or material iteration, the Project
OS must contain an active Work Object ID, a Task Contract with objective/scope/
exclusions, the relevant state/context package, acceptance boundaries, a
candidate state transition, and a task prompt/dispatch that references these
artifacts. If any item is missing, the agent must stop and request the missing
contract before starting work.

There may be exactly one active Work Object in `CURRENT_WORK.md`; when no work
is active, the latest closed Work Object must say so explicitly. Earlier objects
must be explicitly marked archived/superseded and may not retain an active
state label. Every material claim must identify its evidence layer:
local-uncommitted, committed, remote reference, GitHub Release object, or
Founder acceptance. Run `python3 scripts/check_company_os_consistency.py`
before Founder review or release review; a failure blocks the review until the
records are reconciled.

This is a reusable Company OS v0.1 rule for every project instance, not an
automatic background mechanism. v0.1 is manual: Codex follows it when the task
prompt or dispatch is constructed with these artifacts. A future Company OS
runtime could enforce it automatically, but v0.1 cannot.

For any state-changing version, gate, or release task, the dispatch must first
identify the active Work Object ID, current State Package/reference, scope, and
stop condition. If no active Work Object exists, the task must not proceed as a
normal execution task; create or activate the Work Object first.

## Result Package and write-back contract

Every Work Object completion must record:

- objective, scope, constraints and exclusions;
- actual result, evidence references, validation status and known limitations;
- candidate state transition and the founder decision required;
- a write-back checklist: update `PROJECT_STATE.md`, the active Work Object,
  `DECISIONS.md` and `EVALUATIONS.md` only after the founder accepts the
  transition, then record the acceptance evidence and date.

Before acceptance, a work object is `candidate-complete` or `awaiting-founder`
and the project state remains unchanged. An agent may prepare proposed
write-back text, but only the founder's explicit acceptance authorizes changing
accepted project state.

Completion is governance-complete only after: execution → Result Package →
verification → founder acceptance where required → Company OS write-back. A
release additionally requires a final post-push reconciliation after all
intended pushes. Record separately the release tag name, tag object, tag target,
local branch HEAD, remote branch HEAD, and GitHub Release-object status.

Release identity is immutable (version, tag, tag target, and benchmark/protocol
fingerprints). Repository state is mutable (current branch HEAD, remote branch
HEAD, active Work Object, and worktree). Never substitute the latest commit for
the release tag target. If Git or remote state differs from Company OS after a
state-changing task, mark the record `STALE / OUT-OF-SYNC` until reconciled.

For a release, the Result Package must additionally include the release commit
SHA, annotated tag object and peeled commit, branch push verification, remote
reference verification, repository status, validation evidence, and a clear
statement about whether a GitHub Release object exists. A Git tag is a Git
reference; it is not the same thing as a GitHub Release object. Release
completion requires founder acceptance followed by structured write-back.

The minimum release write-back is to update `PROJECT_STATE.md`, the active
Work Object, `DECISIONS.md`, and `EVALUATIONS.md`; record acceptance evidence
and date; record branch/tag remote references; and record remaining
limitations. If a remote reference or release-object check is unavailable,
the release remains candidate-complete rather than silently becoming accepted
state.

The Retrieval Platform is the first validation project. This protocol records
verified history, candidate work, and founder decisions without inferring one
from another.

The Founder accepted the v0.5.0 release and its post-release review, then
accepted the bounded v0.5.1 Gate 5 closure and authorized v0.5.1 release.
v0.5.1 is now released and closed; no active Work Object exists. A successor
gate or version requires a new Start Gate and explicit Founder authorization.

See [PROJECT_STATE.md](PROJECT_STATE.md), [CURRENT_WORK.md](CURRENT_WORK.md),
[DECISIONS.md](DECISIONS.md), and [EVALUATIONS.md](EVALUATIONS.md). The
latest closed release contract is
[V051_RELEASE_START_GATE.md](V051_RELEASE_START_GATE.md); the latest
synchronization record is
[GOVERNANCE_AUDIT_2026-08-17.md](GOVERNANCE_AUDIT_2026-08-17.md).
