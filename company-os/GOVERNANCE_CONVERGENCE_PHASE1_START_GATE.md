# GOV-CONV-001 — Retrieval Governance Convergence Phase 1

**Project:** `armie-retrieval-platform`
**Work Object:** `GOV-CONV-001`
**Start Gate:** accepted for bounded execution by Founder authorization on 2026-08-30
**Core:** ARMIE Company OS Core — Governance Convergence Standard v0.1

## Objective

Make Retrieval Platform the first reference implementation of ARMIE’s common
governance interface, without changing retrieval behavior, version scope,
evaluation results, release state, or product code.

## Scope

Allowed changes are limited to `AGENTS.md`, `company-os/`, and
`scripts/check_company_os_consistency.py`:

- add a source-pointed `GOVERNANCE_SURFACE.md`;
- map it through the local Project Adapter and Agent entrypoint;
- make the consistency checker validate the common governance interface; and
- return a Result Package with evidence and a proposed portfolio write-back.

## Exclusions

- No `src/`, `services/`, Workbench, retrieval, planner, ranking, C1,
  Dataset, benchmark, evaluation, or API behavior changes.
- No CI workflow change, external-provider call, benchmark run, cloud action,
  release, tag, GitHub Release operation, commit, push, merge, or v0.6 work.
- No Founder acceptance inferred or recorded from this Start Gate.

## Preconditions and truth boundary

- Remote `origin/main` was independently verified at `bebc34d` before work.
- The original checkout was behind remote and had an unrelated untracked file;
  execution uses an isolated worktree based on verified `origin/main`.
- GitHub remains engineering truth; project-local Company OS records remain
  project governance truth; Company OS Core receives only a material
  portfolio write-back after Founder acceptance.

## Evidence and validation

- Markdown local-link validation for changed governance files.
- `python3 scripts/check_company_os_consistency.py`.
- `git diff --check`.
- Review that the surface does not duplicate mutable GitHub/CI facts or make
  a new release/capability claim.

## Executable readiness

`not_applicable`: this is a documentation/governance-interface alignment task,
not a claimed runtime, benchmark, provider, API, migration, or deployment
capability. Future executable Work Objects must use the Core Traceability
Matrix and no-model smoke requirements.

## Candidate transition and stop condition

Candidate transition: `PENDING_ALIGNMENT → READY_FOR_FOUNDER_ACCEPTANCE` for
the Retrieval governance-interface sample only.

Stop after the Result Package and candidate local records are prepared. Do not
mark the sample accepted, update portfolio alignment to `DIRECT`, commit, push,
or start another Work Object without an explicit Founder decision.
