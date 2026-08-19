# Retrieval Platform Project Adapter — Company OS Core v0.1

**Project ID:** `armie-retrieval-platform`

**Core reference:** ARMIE Company OS Core v0.1 at
`/Users/ting/Documents/New project/armie-company-os-core/`.

The Core is a shared reference, not a source to copy and not a replacement for
the local project records. The Retrieval Platform adapter preserves this
repository’s history, gates, benchmark evidence, and acceptance boundaries.

## Local mappings

| Core primitive | Retrieval Platform record |
|---|---|
| Project State | `company-os/PROJECT_STATE.md` |
| Work Object / Task Contract | `company-os/CURRENT_WORK.md`, `AGENTS.md`, and scoped gate documents |
| Evidence / Evaluation | `company-os/EVALUATIONS.md`, `docs/`, `tests/`, benchmark artifacts |
| Decision / Risk / Open Question | `company-os/DECISIONS.md`, `PROJECT_STATE.md`, `CURRENT_WORK.md` |
| Candidate / Acceptance | Work Object candidate transition, Result Package, founder decision |
| Committed / Released | exact Git commit/ref and release write-back in local records |

## Entry and handoff

Material work must enter through the Core Start Gate and the local `AGENTS.md`
rules. The active Work Object and Task Contract remain the local authority.
Each completion returns a Result Package with evidence, candidate transition,
acceptance status, risks/open questions, write-back destination, and release
verification status where relevant.

The adapter introduces no shared Git history, release object, runtime state, or
cross-project synchronization mechanism.
