# Latest Closed Work Object — CI Revival 2026-08

**Work Object:** `ci-revival-2026-08`
**State:** closed / merged
**Authority:** Founder (repo owner) reviewed and explicitly authorized this
Company OS write-back and the merge of PR #1 in this session (2026-08-26).
This acceptance is recorded because the Founder gave it directly in this
dispatch, not inferred from prior agent execution or CI passing on its own.

**Task Contract / Start Gate:** delivered externally as
`claude-code-instructions-ci-revival.md` and `spec-ci-revival.md` (Work
Object `ci-revival-2026-08`); the spec's Section 6 acceptance criteria and
Section 5 invariants served as the Task Contract for this session.

## Objective and scope

Restore a passing CI baseline on the already-released v0.5.1 `main`
(`0709767`) using only test-harness and CI-configuration changes — no
change to `src/armie_retrieval/` or `services/` retrieval, planning,
ranking, or evaluation behavior. GitHub Actions CI (`ci.yml`) had failed on
every tagged release from v0.3.0 through v0.5.1.

**In scope:** `.github/workflows/ci.yml`, `Makefile`, `pyproject.toml`,
`tests/test_workbench_api.py`, `tests/test_workbench_startup.py`, plus two
narrowly-scoped follow-up fixes surfaced by CI and code review after the
initial patch (see below). **Out of scope (untouched):**
`src/armie_retrieval/`, `services/`, retrieval/planning/ranking behavior,
`apps/workbench/` frontend Playwright CI wiring, and Company OS backfill —
the last of which is this record itself, completed as a distinct, explicitly
authorized follow-up per Codex's P1 review comment on PR #1, not silently
bundled into the CI-fix commits.

## Root causes fixed

1. `tests/test_v040_dense_index_builder.py` used pytest-style `tmp_path`
   fixtures that `unittest`'s TestLoader silently collects zero tests from,
   and `pytest` was undeclared, causing an `ImportError`. Added `pytest` as
   a `dev` extra and a dedicated CI pytest step; `unittest discover`
   unchanged for the other 32 test files.
2. `tests/test_workbench_api.py::test_health_capabilities` hardcoded
   `package_version`/`frontend_version`/`application_version == "0.5.0"`
   against a 0.5.1 package, and a masked companion assertion assumed a
   `pip install .` source-tree layout. Now compares against
   `armie_retrieval.__version__` and the site-packages-compatible path
   suffix.
3. `test_score_semantics_and_execution_context` assumed a local Ollama
   daemon and cached BGE cross-encoder weights, unavailable on any
   GitHub-hosted runner. Split into an always-on baseline assertion, a new
   `ARMIE_RUN_MODEL_ENHANCED_INTEGRATION=1`-gated ideal-path test (same
   convention as the existing Elasticsearch integration gate), and a new
   always-on `test_model_enhanced_falls_back_without_ollama` asserting the
   documented fallback degrades explicitly.
4. `test_direct_backend_diagnostic_from_repository_root_without_path_injection`
   assumed `import armie_retrieval` fails without `PYTHONPATH`, but `ci.yml`'s
   own `pip install .` step installs the package first, making that
   precondition false in CI. Now skipped only when a runtime probe verifies
   the precondition provably cannot hold.
5. (Follow-up, surfaced by the first green 3.11 run unblocking a previously
   fail-fast-cancelled 3.9 leg) `src/armie_retrieval/contracts.py`'s PEP 604
   `str | None` pydantic v2 fields raised `TypeError` on Python 3.9 without
   `eval_type_backport`; added as a base dependency, marker-gated to
   `python_version < "3.10"` — a no-op on 3.10+. `tests/test_workbench_api.py`
   needs `httpx` for `fastapi.testclient`, previously declared only under the
   unused-by-CI `workbench` extra; added to `dev` instead.
6. (Follow-up, Codex automated review comment on PR #1,
   `discussion_r3862099960`/comment id `3862099960`)
   `test_model_enhanced_falls_back_without_ollama` could silently no-op-pass
   on any runner where Ollama/BGE are both reachable (verified true of this
   development environment itself). Fixed to skip explicitly, with a stated
   reason, only when both providers resolved to their non-fallback path —
   i.e. only when there is genuinely nothing to observe.

## Evidence

- Pull request:
  [tosspro23-cell/armie-retrieval-platform#1](https://github.com/tosspro23-cell/armie-retrieval-platform/pull/1)
- Commits on `fix/ci-revival-2026-08`: `02a816a` (fixes 1–4), `05a6f8e`
  (fix 5), `edb80ee` (fix 6), plus this write-back commit.
- Passing CI run, both matrix legs, at `edb80ee` (the commit merged to
  `main`):
  [pull_request run](https://github.com/tosspro23-cell/armie-retrieval-platform/actions/runs/32962285779)
  and
  [push run](https://github.com/tosspro23-cell/armie-retrieval-platform/actions/runs/32962281664) —
  both `test (3.9)` and `test (3.11)` jobs `success`.
- Local verification (this session): `pip install ".[dev]"` +
  `python -m unittest discover -s tests -v` — 196 tests, 0 failures;
  `PYTHONPATH=src python -m pytest tests/test_v040_dense_index_builder.py -v`
  — 3 passed; `python examples/expert_discovery_demo.py` exits 0.

## Candidate transition and Founder decision

The Founder reviewed PR #1 in this session, requested this Company OS
write-back explicitly, and separately authorized merging PR #1 into `main`
with a regular merge commit (not squash/rebase) in the same dispatch. This
Work Object is closed on merge. It does not authorize v0.6, any new
capability, or any change to retrieval/planning/ranking/C1 behavior — none
of `src/armie_retrieval/` or `services/` was touched by this Work Object.

## Structured write-back checklist

- [x] Root causes and fixes recorded, referencing PR #1 and its commits.
- [x] CI evidence (both matrix legs, both trigger events) recorded.
- [x] Codex automated review disposition recorded: one finding fixed
      (`3862099960`), one finding explicitly declined as out of this Work
      Object's scope per the spec's own deferred-follow-up section
      (`3862099954` — Company OS backfill itself, completed here instead as
      an explicit, separate, Founder-visible step).
- [x] Founder authorization for write-back and merge recorded in this
      session.
- [x] Post-merge `main` HEAD, branch reconciliation, and post-merge CI
      status are reported directly to the Founder in this session per the
      Founder's own dispatch; no release-style immutable identity (tag,
      GitHub Release object) applies to this bounded CI/test-harness fix,
      so no further Company OS file write-back is required beyond this
      record.

---

## Archived Work Object — v0.5.1 Release Stabilization and Closeout

**Work Object:** `armie-retrieval-v051-release-stabilization-closeout`
**State:** released / closed
**Authority:** Founder acceptance of Gate 5, Gate 5-F/F2/F3 closure, frozen
v0.5.1 capability boundary, and explicit release/GitHub-publish authorization.

**Task Contract / Start Gate:** [v0.5.1 release contract](V051_RELEASE_START_GATE.md)

**Release Result Package:** release commit
`c4bf57fd4ead76cdc18a36e885eea9a5215401a4`; annotated tag object
`6ef90af0b76add2186cd31ef0d74150665234bf8`; tag target
`c4bf57fd4ead76cdc18a36e885eea9a5215401a4`; verified pushed on `origin/main`
and retained in its history; and published GitHub Release
[`v0.5.1`](https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1).

**Validation evidence:** default Python regression suite, focused live
Elasticsearch/backend checks, frontend unit tests and production build, package
build, Markdown-link checks, Company OS consistency check, and `git diff
--check` passed. The isolated live Workbench check passed all 16 Founder-critical
Playwright scenarios against the existing local v0.5-compatible Elasticsearch
projection.

## Objective and scope

Stabilize, validate, publish, and close v0.5.1 only. The frozen capability is
governed natural-language intent resolution through clarification, explicit
resolution and confirmation, then the existing deterministic C1
`RetrievalContract`/Elasticsearch execution path with provenance. This Work
Object may update release metadata, documentation, Company OS records, and
release identity; it may not add a feature, retune interpretation, change C1,
ranking, Dataset v2, or benchmark behavior.

## Release Work Package

- [Release contract and reconciliation](V051_RELEASE_START_GATE.md)
- [Gate 5 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md)
- [Release notes](../docs/v0.5.1/release-notes.md)
- `apps/workbench/tests/gate7c.integration.spec.ts` — live Founder-critical
  verification, including positive, executed-zero, stale-state, and manual C1
  paths

## Candidate transition and founder decision

The Founder accepted Gate 5 and authorized the bounded release. Post-push
remote and GitHub Release-object evidence is now recorded above. This Work
Object is closed. No active Work Object exists; v0.6 and all next-version work
remain inactive and unauthorized until a new Start Gate is explicitly accepted.

## Structured write-back checklist

- [x] Gate 5/F/F2/F3 acceptance and frozen scope recorded.
- [x] Release Work Object and Task Contract activated.
- [x] Worktree reconciliation and release-content classification complete.
- [x] Release-critical validation complete against the committed candidate.
- [x] Release commit, annotated tag, and remote refs verified.
- [x] GitHub Release-object published and recorded.
- [x] Company OS post-push state written back as released/accepted/closed.
- [x] v0.6 remains not started.

---

## Archived Work Object — v0.5.1 Gate 5-F3

**Work Object:** `armie-retrieval-v051-gate5-f3-confirmed-result-rendering`
**State at closure:** Founder-accepted as part of Gate 5 closure.

The F3 Result Package documented canonical confirmed-execution rendering,
positive and executed-zero result states, and 16 live Founder-critical
Playwright checks. It is preserved at
[`docs/v0.5.1/gate5-confirmed-c1-e2e.md`](../docs/v0.5.1/gate5-confirmed-c1-e2e.md).
It no longer authorizes a separate active task.

---

## Historical Work Object Archive (not active)

The sections below preserve prior Work Objects, Task Contracts, and Result
Packages as historical evidence. They are superseded records, not active work.
Only the Gate 5-F3 Work Object at the top of this file is current. A new active
object requires a new Start Gate and explicit Founder authorization where
required.

## Archived Work Object — v0.5.1 Gate 3J

**Work Object:** `armie-retrieval-v051-gate3j-clarification-protocol`
**State:** candidate-complete / clarification architecture candidate; Founder acceptance pending; Gate 4 inactive
**Authority:** founder Gate 0/Gate 1 acceptance, explicit Gate 2 acceptance as
an experimental result, explicit Gate 3 authorization, P0 carry-forward
conditions, and the Gate 3 Task Contract

## Objective

Create and execute one frozen prospective staged-interpretation promotion
benchmark against the deterministic candidate without executing C1 or
integrating Workbench.

## Accepted Gate 3G-R Result Package

- Benchmark admission passed: 160 rows, 0 exact duplicates, 0 near-duplicate
  pairs, 33 pattern families, and 10 compositional rows.
- Candidate executed exactly once after the v2 contract was frozen.
- Candidate thresholds failed: role accuracy 38.75%, False REQUIRED 1.25%,
  mapping 71.88%, and unsupported preservation 36%.
- Evidence: [Gate 3G-R contract](../docs/v0.5.1/gate3gr-promotion-contract-v2.md)
  and [results](../docs/v0.5.1/gate3gr-promotion-results.md).
- Candidate transition: **Decision B — no promotion**; Gate 4 remains inactive.

Founder accepted Gate 3G-R and Decision B (no promotion). Agents cannot infer
promotion from that acceptance or authorize Gate 4.

## Accepted Gate 3H Result Package

- Objective: bounded Stage 1/2 model capability study using development-only
  evidence while preserving deterministic Stages 3–6.
- Evidence: [Gate 3H results](../docs/v0.5.1/gate3h-model-capability-results.md).
- qwen3:4b remains phrase-contract invalid/incomplete. qwen3:8b completed
  36/36 calls but produced token-level spans: exact phrase precision 0.99%,
  recall 2.70%, role accuracy 0%, False REQUIRED 13.89%, False EXCLUDED 25%.
- Candidate transition: **Decision C — no model-assisted candidate**; Gate 4
  remains inactive.
- Founder accepted Gate 3H Decision C; no model-assisted candidate was created.

Founder accepted Gate 3H Decision C and authorized Gate 3I. No model-assisted
candidate was promoted.

## Accepted Gate 3I Result Package

- Objective: test deterministic Stage 1 span proposals plus qwen3:8b-only
  Stage 2 role classification on development evidence.
- Evidence: [Gate 3I results](../docs/v0.5.1/gate3i-role-only-results.md).
- Result: 61/61 spans completed with 100% schema validity; role accuracy
  55.74%, False REQUIRED 32.79%, False EXCLUDED 1.64%. Context, unsupported,
  and ambiguous phrases remained unsafe.
- Candidate transition: **Decision B — improvement is real but insufficient**;
  Gate 4 remains inactive.
- Founder accepted Gate 3I Decision B; no unrestricted Stage 2 architecture was promoted.

Founder accepted Gate 3I Decision B. No unrestricted Stage 2 architecture was
promoted.

## Gate 3J Result Package

- Objective: define and validate deterministic clarification-state and
  user-resolution protocol without UI, chat agent, C1, or Gate 4.
- Evidence: [Gate 3J clarification protocol](../docs/v0.5.1/gate3j-clarification-protocol.md)
  and `tests/test_v051_gate3j_clarification.py`.
- Result: versioned ClarificationItem/Resolution schemas, bounded taxonomy,
  blocking lifecycle, deterministic resolution/edit/remove/dependency semantics,
  provenance, confirmation boundary, and no-clarification fast path implemented
  and tested.
- Candidate transition: clarification architecture candidate; Gate 4 remains
  inactive.
- Founder decision required: accept/reject Gate 3J Result Package and authorize
  any future clarification/confirmation Workbench UX Gate.

## Input state

- Release tag: `v0.5.0`
- Tag target/release commit: `05e661f`
- Final local and remote `main`: `f181960`
- P0: accepted with carry-forward conditions
- Gate 0: founder-accepted
- Gate 1: founder-accepted
- Gate 2: founder-accepted as an experimental result; Outcome E
- Gate 3: authorized and active
- Gate 4: inactive
- Tag object: `b4230aee`
- GitHub Release object: not created or independently verified

## Scope and constraints

Included a new frozen evaluation benchmark, pre-registered promotion criteria,
full-arm comparison, repeatability/paraphrase studies, failure taxonomy, and
Result Package. Excluded Workbench, C1 execution, production NL API, released
data changes, C1 semantic changes, Gate 4, v0.6, commit, tag, and push.

## Release Result Package

Release commits: `5425b2e`, `a42789d`, `0102cdb`, `05e661f`, and follow-up
closeout `f181960`. Validation recorded in
[v0.5.0 release notes](../docs/v0.5.0/v0.5.0-release-notes.md) and the
[post-release closeout](../docs/v0.5.0/post-release-closeout.md): Python 131
passed/3 skipped, Elasticsearch 2 passed, frontend 5 passed, canonical and
founder Playwright 30 passed each, package build passed, and Markdown/diff
checks passed.

P0 was accepted with carry-forward conditions, Gate 0 and Gate 1 were accepted,
and Gate 2 was authorized. Gate 2 evidence is recorded in the [Gate 2 Result
Package](../docs/v0.5.1/gate2-extraction-baseline-comparison.md).
The P0 raw coverage and historical mapping-fingerprint conditions remain
carried forward to later data/index work; they are not silently closed here.

## Acceptance and disposition

Gate 7 received final founder acceptance, Gate 8 release readiness passed, and
Gate 9 completed the accepted v0.5.0 engineering/Git release. The tag remains
fixed to `05e661f`; `f181960` is the later branch closeout commit. The founder
authorized v0.5.1 Gate 0 with P0 carry-forward conditions, accepted Gate 0 and
 Gate 1, accepted Gate 2 as an experimental result (Outcome E), accepted Gate
 3C evidence with architecture decision D (no promotion), and authorized Gate
 3D. Gate 3D and Gate 3E are accepted; Gate 3F is authorized for
 development-only staged validation. No extractor is promoted and Gate 4
 remains inactive.

## Structured write-back checklist

- [x] Objective, scope, constraints and exclusions recorded.
- [x] Release Result Package and validation evidence recorded.
- [x] Founder acceptance and final disposition recorded.
- [x] Immutable tag identity separated from mutable branch state.
- [x] Remote branch/tag and GitHub Release-object status recorded.
- [x] PROJECT_STATE, CURRENT_WORK, DECISIONS and EVALUATIONS updated.
- [x] Start Gate, completion write-back, post-push reconciliation and drift
      rules strengthened.
- [x] P0 Result Package accepted with carry-forward conditions.
- [x] Gate 0 and Gate 1 acceptance and Gate 2 authorization recorded.
- [x] Gate 2 scope, arms, acceptance criteria, and stop condition recorded.
- [x] Gate 2 Result Package and comparison artifact prepared.
- [ ] Final Gate 2 test/static verification complete (focused Gate 2 tests,
      compilation, links and diff checks pass; repository-wide suite remains
      blocked by absent external v0.5.0 Workbench benchmark artifacts, as
      recorded in the Result Package).
- [x] Gate 2 accepted as an experimental result with Outcome E.
- [x] Gate 3 authorization recorded from the founder prompt.
- [x] Gate 3 benchmark and promotion criteria frozen before arm results.
- [x] Gate 3 Result Package and failure analysis prepared.
- [x] Gate 3 focused/full-suite/static verification completed.
- [x] Gate 3C model/hybrid full-set coverage and repeatability complete via the
      resumable checkpointed harness; 120/120 terminal for each arm, with no
      infrastructure or structured-output failures.
- [x] Frozen model/hybrid semantic metrics computed without changing thresholds;
      both arms fail promotion criteria as recorded in the Gate 3C Result Package.
- [x] Gate 3C evidence accepted and architecture decision D (no promotion)
      recorded.
- [x] Gate 3D Rule v3, Model v2, and Cascade v2 refinement and frozen rerun
      recorded.
- [x] Gate 3D semantic Result Package accepted; architecture decision D (no
      promotion) recorded.
- [x] Gate 3E architecture reassessment prepared without implementation
      changes.
- [x] Gate 3E acceptance and Path A staged-architecture direction recorded.
- [x] Gate 3F staged schemas, development fixture, deterministic baseline,
      metrics, and Result Package prepared.
- [x] Gate 3F tests, full regression suite, links, and diff checks completed.
- [ ] Founder accepts or rejects the Gate 3F Result Package.
- [ ] Gate 4 authorization (not started).

## Candidate next transition

`v0.5.1 Gate 3F → Gate 4 READY only after founder accepts or rejects the Gate
3F Result Package and provides a new Gate 4 authorization`. Gate 4 remains
inactive.

## Historical Gate 3E Work Object

**State:** completed / founder-accepted
**Objective:** Decompose Gate 3D failures and reassess interpretation architecture.
**Scope:** Evidence review and architecture recommendation only; no code,
prompt, benchmark, threshold, model, runtime, C1, Workbench, or Gate 4 work.
**Evidence:** [Gate 3E architecture reassessment](../docs/v0.5.1/gate3e-architecture-reassessment.md).
**Candidate transition:** Gate 3E accepted; Gate 4 remains inactive.
**Disposition:** Path A selected; Gate 3F separately authorized.

## Gate 3F Task Contract

**Objective:** Design and validate a bounded staged interpretation pipeline on
development-only evidence. **Scope:** typed span detection, semantic role,
registry mapping, normalization, deterministic validation, and non-executable
CandidateInterpretation assembly. Explicit-requirement-only is the interim
safety boundary. No stronger model, frozen-120 tuning, C1/Workbench,
RetrievalContract, Gate 4, commit, tag, or push.

**Acceptance boundaries:** preserve the frozen benchmark; use a separately
identified development fixture; report stage metrics, error propagation,
latency, and deterministic/model-assisted comparison; stop at
READY_FOR_FOUNDER_ACCEPTANCE.

## Gate 3F-R Result Package

Evidence: [Gate 3F-R refinement report](../docs/v0.5.1/gate3fr-stage2-refinement.md).
The deterministic arm met the development safety and role targets on the new
36-case prospective fixture. The qwen3:4b arm completed through a resumable
harness, but phrase-level role output was malformed, so its comparison is
invalid/incomplete. Candidate transition: Gate 3F-R
READY_FOR_FOUNDER_ACCEPTANCE; Gate 4 remains inactive.

## Historical Gate 3G Result Package

Evidence: [Gate 3G promotion results](../docs/v0.5.1/gate3g-promotion-results.md).
The deterministic candidate executed once on the frozen 180-item benchmark,
but quality audit found 122 duplicate normalized requests. The run is
invalidated; the benchmark is not edited and no rerun is authorized.
Candidate transition: Gate 3G EVIDENCE_INVALID; Gate 4 remains inactive. This
historical package is superseded by the Gate 3G-R package below.
