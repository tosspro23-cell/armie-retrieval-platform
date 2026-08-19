# ARMIE Company OS Evidence Index

## Current-state precedence (2026-08-17)

This file indexes evidence; it is not the sole current-state authority.
`PROJECT_STATE.md` and the top Work Object in `CURRENT_WORK.md` supersede
historical snapshots below. Entries that say candidate/active for earlier
Gate 3J, Gate 4, or Gate 5 phases describe their state at capture and must not
override the accepted decisions recorded in `DECISIONS.md`.

Current status: Gate 3J, Gate 4, and Gate 5 are Founder-accepted. v0.5.1
release stabilization/closeout is released and closed: commit `c4bf57f`,
annotated tag `v0.5.1`, verified `origin/main`, and a published
[GitHub Release](https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1).
There is no active Work Object. v0.6 remains inactive.

## v0.5.1 release Result Package

- `c4bf57f` — frozen v0.5.1 release commit, pushed and retained in `main`
  history.
- `v0.5.1` — annotated tag object `6ef90af0`, peeled commit `c4bf57f`.
- [Release notes](../docs/v0.5.1/release-notes.md) and
  [published GitHub Release](https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1).
- Default Python regression, focused Elasticsearch/backend checks, frontend
  unit/build, package build, Markdown links, governance consistency, and diff
  checks passed. The isolated live Workbench validation passed 16/16
  Founder-critical Playwright scenarios.

This is a bounded governed-interpretation release. It does not validate
unrestricted semantic interpretation, change C1/ranking/Dataset v2/benchmark
semantics, or authorize v0.6.

## Gate 5

- `docs/v0.4.0/gate5-results.md` — relevance metrics, failure analysis and
  benchmark scope.
- `docs/v0.4.0/dataset-card.md` — v1 dataset limitations and provenance.
- `docs/v0.4.0/validation-report.md` — Gate 5 validation narrative and limits.

Gate 5 is a controlled synthetic relevance benchmark. Its metrics do not prove
validated real-world expert-network search quality.

### Gate 5 live C1 evidence (candidate Result Package)

- `docs/v0.5.1/gate5-confirmed-c1-e2e.md` — live service/index identity and
  bounded scenarios.
- Local Elasticsearch 8.15.3: alias `armie-experts-v0.5-dense` resolved to
  `armie-experts-v1-v2-gate6b-dense-10000` (10,000 documents); C1 compatibility
  accepted with BAAI/bge-m3/1024 dimensions.
- Confirmed interpretation, numeric/seniority/conjunction/exclusion,
  unsupported relationship, strict shortfall, and all-hard-removed flows were
  exercised. The initial browser file was 8/9 while the payload was absent;
  after Gate 5-R restoration the exact rerun was 9/9 and Dataset v2 identity
  was reported.

This is runtime/protocol evidence only; it does not claim new Gold/Silver
metrics. Gate 5-R restored the payload with the canonical generator and
verified checksum `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`.
The exact founder-environment browser path then passed 9/9, eliminating the
Legacy v1 fallback. Gate 5 remains unaccepted pending the Founder manual test.

## Gate 5.5A

- `docs/v0.4.0/dataset-v2-design.md` — versioned v2 design and pipeline
  separation.
- `docs/v0.4.0/dataset-v2-pilot-audit.md` — pilot audit summary.
- `docs/v0.4.0/dataset-v2-pilot-audit.json` — tracked machine-readable summary.
- `/tmp/armie-v040-dataset-v2-pilot/audit.json` — full generated audit,
  including manual inspection samples.
- `docs/v0.4.0/dataset-card-v2.md` — v2 provenance and limitations.
- `tests/test_v040_dataset_v2.py` — deterministic, separation, integrity and
  quality-gate tests.

Gate 5.5A evidence supports a pilot result only. Gold is an independent
structured audit, not external human ground truth; Silver remains explicitly
rule-assisted. The benchmark must not be generalized to natural expert-network
data.

## Gate 5.5B

- `docs/v0.4.0/gate55b-results.md` — completed v1/v2 benchmark results,
  boundaries, timing and limitations.
- `docs/v0.4.0/benchmark-stability-report.md` — stability comparison and
  interpretation limits.
- `docs/v0.4.0/dataset-v2-full-audit.md` — full Dataset v2 integrity audit.
- `58baad4` — dense-index resumability checkpoint.
- `9973367` — committed benchmark stability checkpoint.

Gate 5.5B is completed evidence, not external validation. The corpus remains a
controlled synthetic relevance benchmark with templated language and leakage
risk.

## Gate 6 — accepted Result Package

- `docs/v0.4.0/validation-report.md` — Gate 6 scope and verification summary.
- `README.md` — Workbench usage and artifact boundary.
- `apps/workbench/tests/gate6.acceptance.spec.ts` — 17 Chromium browser
  acceptance checks after the bounded UX polish.
- `tests/test_workbench_api.py` — backend benchmark-library and execution
  regression coverage.
- `CURRENT_WORK.md` — historical candidate Result Package and write-back
  checklist, superseded by the accepted release work object.

Gate 6 evidence is verified, founder-accepted, and committed at `5ee33a1`.
It validates Workbench mechanics and preserves existing runtime semantics; the
underlying benchmark remains controlled synthetic evidence.

## Gate 7 — v0.4.0 release Result Package

- `company-os/CURRENT_WORK.md` — release Result Package, remote references and
  structured write-back checklist.
- `docs/v0.4.0/release-notes.md` — accepted release scope and limitations.
- `docs/v0.4.0/validation-report.md` — final validation matrix and identity
  evidence.
- `266bf5b` — release commit on `main`.
- `v0.4.0` — annotated tag object `f30b5352`, peeled commit `266bf5b`.
- `git ls-remote origin` — branch and tag verified remotely.
- GitHub Releases API `/releases/tags/v0.4.0` — HTTP 404; no GitHub Release
  object exists.

Gate 7 release evidence is founder-accepted and pushed. The release is the
Expert Discovery Relevance Engineering Foundation, not a claim of natural
expert-network quality, external human ground truth, or production SaaS
readiness.

## v0.5.0 Gate 2/2C — candidate evidence

- `docs/v0.5.0/dataset-v2-field-profile-evidence.md` — reproduced 10K field
  completeness evidence and frozen checksum.
- `docs/v0.5.0/constraint-projection-design.md` — versioned nested projection.
- `docs/v0.5.0/gate2-compiler-review.md` — compiler scope, semantic plan and
  isolated Elasticsearch 8.15.3 proof.
- `src/armie_retrieval/contracts.py` — contract semantics and validation.
- `src/armie_retrieval/indexing/constraint_projection.py` — deterministic
  projection.
- `src/armie_retrieval/constraints/compiler.py` — bounded compiler.
- `tests/test_v050_retrieval_contract.py` and
  `tests/test_v050_projection_compiler.py` — focused regression coverage.

This was candidate evidence before the accepted v0.5.0 release and is no
longer the active work object. It must not be read as an unaccepted current
state.

## v0.5.0 Gate 9 — accepted release Result Package

- `docs/v0.5.0/gate6d-benchmark-results.md` and
  `docs/v0.5.0/gate6d-evaluation-protocol.md` — formal constraint
  evaluation evidence and protocol.
- `docs/v0.5.0/gate7d-manual-acceptance.md` — founder product acceptance.
- `docs/v0.5.0/gate8-release-readiness.md` — release readiness and scope.
- `docs/v0.5.0/post-release-closeout.md` — release Result Package and
  limitations.
- `5425b2e`, `a42789d`, `0102cdb`, `05e661f` — controlled release commits.
- `f181960` — follow-up closeout documentation commit.

Release identity: annotated `v0.5.0` tag object `b4230aee`, peeled target
`05e661f`; final local and remote `main` `f181960`. The Git tag is pushed;
no GitHub Release object was created or independently verified.

Final regression matrix: Python 131 passed/3 skipped; Elasticsearch 2 passed;
frontend 5 passed; canonical Playwright 30 passed; founder-environment
Playwright 30 passed; package build passed; Markdown links 88 checked/0
broken; `git diff --check` passed.

The release proves the bounded structured-constraint retrieval scope only. It
does not establish natural-language contract extraction, general temporal or
relationship semantics, production C2/C3, or natural expert-network quality.

## v0.5.0 post-release architecture review

- `docs/v0.5.0/post-release-architecture-review.md` — bounded review Result
  Package covering proven/unproven capabilities, evaluation and productization
  lessons, technical debt, and the proposed v0.5.1 boundary.

Disposition: **READY_FOR_FOUNDER_ACCEPTANCE**. The review recommended a
prerequisite-bounded v0.5.1 Governed Natural Language → RetrievalContract
direction. P0 was subsequently accepted with carry-forward conditions and Gate
0 was authorized as bounded architecture/specification work.

## v0.5.1 P0 — candidate Result Package

- `docs/v0.5.1/p0-runtime-contract-stabilization.md` — runtime identity,
  compatibility, registry, provenance, coverage, and Gate 0 entry contract.
- `tests/test_v051_p0_runtime_contract.py` — bounded identity/registry/
  provenance regression tests.
- Logical index `armie-experts-v0.5-dense` resolves to the preserved physical
  Gate 6B index with 10,000 documents on local Elasticsearch 8.15.3.

P0 was accepted with carry-forward conditions. Raw structured corpus prevalence
and the historical mapping fingerprint remain later-stage evidence debt.

## v0.5.1 Gate 0 — candidate Result Package

- `docs/v0.5.1/gate0-nl-contract-charter.md` — bounded problem statement,
  architecture boundary, semantic intent/HARD/SOFT/unsupported policy,
  ambiguity and contradiction handling, confirmation, registry dependency,
  interpretation provenance, safety model, evaluation layers, metric families,
  annotation strata, strategy hypothesis, non-goals, and Gate 1 entry contract.
- Founder authorization is recorded with P0 accepted-with-carry-forward
  conditions.

Gate 0 was accepted by the founder. It remains architecture/specification
evidence only; no extractor, model call, benchmark instance, Dataset v2
mutation, C1 change, or Gate 1 work was included in that gate.

## v0.5.1 Gate 1 — candidate Result Package

- `docs/v0.5.1/gate1-interpretation-benchmark-design.md` — schema identity,
  annotation semantics, states, safety metrics, benchmark strata/splits,
  artifact separation, Gate 2 output contract, and non-goals.
- `docs/v0.5.1/gate1-benchmark-manifest.json` — benchmark family, schema,
  registry, strata, split and fingerprint policy.
- `src/armie_retrieval/interpretation/` — non-executable candidate schema,
  deterministic evaluator, and canonical fingerprint helpers.
- `tests/fixtures/v051_gate1_gold.jsonl` — eight-item hand-reviewable fixture.
- `tests/test_v051_gate1_interpretation.py` — slot-level truth tests including
  false-HARD, missed-HARD, mismatch, unsupported, contradiction, and exact
  match cases.

Gate 1 was subsequently accepted by the founder. Its schema/evaluator work did
not implement a production extractor, endpoint, Workbench integration, C1
change, or Gate 2 arm.

## v0.5.1 Gate 2 — candidate Result Package

- `docs/v0.5.1/gate2-extraction-baseline-comparison.md` — bounded comparison,
  safety/correctness metrics, per-stratum observations, error analysis,
  repeatability, latency, and candidate recommendation.
- `docs/v0.5.1/gate2-comparison-results.json` — frozen 20-item development
  fixture comparison artifact.
- `scripts/run_v051_gate2_comparison.py` — deterministic comparison runner;
  interpretation-only, with no C1 or Workbench path.
- `src/armie_retrieval/interpretation/extractors.py` — rule, structured Ollama,
  and conservative hybrid baseline arms.

Gate 2 is candidate-complete pending founder acceptance. The rule arm ran on
all 20 items; model and hybrid arms ran on the same bounded eight-item sample.
The comparison is development evidence, not production readiness or an
accepted extraction architecture.

## v0.5.1 Gate 3 — active evaluation

Gate 2 is now recorded as founder-accepted experimental evidence with Outcome
E. Gate 3 is authorized to create a new frozen evaluation identity, with full
arm coverage, pre-registered safety thresholds, repeatability, paraphrase and
unsupported/contradiction analysis. Gate 4 remains inactive. The Gate 3
Result Package is not yet available.

Current evidence: the frozen 120-item evaluation and manifest are recorded in
`docs/v0.5.1/gate3-frozen-extraction-evaluation.md` and
`docs/v0.5.1/gate3-evaluation-results.json`. The rule arm completed all 120
items but failed the pre-registered safety thresholds (False HARD 9.17%). The
model and hybrid arms attempted 20 items each but completed none because local
Ollama throughput/timeout prevented structured outputs. Result: E / inconclusive;
no extractor promotion and no Gate 4 authorization.

Gate 3B diagnosis is recorded in
`docs/v0.5.1/gate3b-model-coverage.md`: qwen3:4b produced valid warm JSON
responses in minimal tests, but full 120-item serial coverage remained
operationally unsuitable under a fixed 15s timeout/one-retry policy. Gate 3
remains ACTIVE / BLOCKED; no model or hybrid promotion is implied.

## v0.5.1 Gate 3C — resumable model coverage (candidate evidence)

- [Gate 3C report](../docs/v0.5.1/gate3c-resumable-evaluation.md)
- [Gate 3C machine summary](../docs/v0.5.1/gate3c-evaluation-results.json)

The repaired harness durably checkpointed every terminal item and completed the
frozen 120-item qwen3:4b model and hybrid arms (120/120 each, zero infrastructure
or structured-output failures). This closes the execution-coverage blocker, but
not semantic promotion: the model exact match is 0%, precision 30%, recall 30%,
and unsupported preservation 80%; hybrid reproduces the rule profile and fails
the frozen thresholds. Gate 3 is candidate-complete pending founder semantic
decision; Gate 4 remains inactive.

## v0.5.1 Gate 3D — semantic refinement (candidate evidence)

- [Gate 3D report](../docs/v0.5.1/gate3d-semantics-refinement.md)
- [Gate 3D machine summary](../docs/v0.5.1/gate3d-evaluation-results.json)

Gate 3C infrastructure evidence is founder-accepted and architecture promotion
is explicitly D — no promotion. Gate 3D evaluated conservative Rule v3, refined
qwen3:4b Model v2, and safety-first Cascade v2 on the unchanged 120-item
benchmark. Coverage was 120/120 for all arms; Rule v3 and Cascade v2 still
exceeded the 0% False-HARD threshold (6.67%), while Model v2 retained zero
False-HARD but remained at 0% exact, 30% precision, and 30% recall. Gate 3D is
candidate-complete pending founder review; Gate 4 remains inactive.

## v0.5.1 Gate 3E — architecture reassessment (candidate evidence)

- [Gate 3E architecture reassessment](../docs/v0.5.1/gate3e-architecture-reassessment.md)

Gate 3E decomposes the development/frozen gap and documents the Rule
architecture ceiling, qwen3:4b conservative one-shot behavior, and a staged
interpretation recommendation. It made no code, prompt, benchmark, threshold,
model, or runtime changes. The 120-item benchmark remains frozen diagnostic
evidence; Gate 4 remains inactive. This is candidate evidence pending Founder
acceptance, not a promoted architecture.

The Founder subsequently accepted Gate 3E and authorized Gate 3F; the status
above is historical candidate evidence and is superseded by the Gate 3F entry
below.

## v0.5.1 Gate 3F — staged interpretation (active)

Gate 3F is authorized for development-only staged architecture validation. The
frozen 120-item Gate 3 benchmark remains diagnostic and immutable. Evidence
must report stage-level roles, mapping, normalization, validation, error
propagation, and latency without promoting an extractor or entering Gate 4.

## v0.5.1 Gate 3F-R — Stage 2 refinement (active)

Gate 3F-R is authorized for one bounded role-classification refinement and a
new prospective development-validation fixture. Gate 3F remains accepted as
development evidence only; Gate 4 remains inactive.

## v0.5.1 Gate 3G-R — prospective promotion evidence

- [Gate 3G-R contract](../docs/v0.5.1/gate3gr-promotion-contract-v2.md)
- [Gate 3G-R results](../docs/v0.5.1/gate3gr-promotion-results.md)

The benchmark admission audit passed before execution. The deterministic staged
candidate then failed the frozen promotion thresholds. The Founder accepted
Decision B (no promotion); Gate 4 remains inactive.

## v0.5.1 Gate 3H — model capability evidence

- [Gate 3H model capability results](../docs/v0.5.1/gate3h-model-capability-results.md)

Gate 3G-R was Founder-accepted with Decision B. Gate 3H then compared the
deterministic reference with qwen3:4b and qwen3:8b on development-only evidence.
Neither model satisfied the phrase-level contract or safety boundary; Decision
C (no model-assisted candidate) is proposed. Founder acceptance remains
required and Gate 4 remains inactive.

## v0.5.1 Gate 3I — role-only model evidence

- [Gate 3I role-only results](../docs/v0.5.1/gate3i-role-only-results.md)

Gate 3H was Founder-accepted with Decision C and Gate 3I was authorized. The
deterministic Stage 1 plus qwen3:8b-only Stage 2 arm achieved 55.74% role
accuracy with valid schema output, but False REQUIRED was 32.79% and safety
targets failed. Decision B (real but insufficient improvement) is proposed;
Founder acceptance remains required and Gate 4 remains inactive.

## v0.5.1 Gate 3J — clarification protocol evidence

The candidate wording in the original package is a historical snapshot. The
Founder subsequently accepted Gate 3J; see `DECISIONS.md` D-027 and the current
state record.

- [Gate 3J clarification protocol](../docs/v0.5.1/gate3j-clarification-protocol.md)

Gate 3I was Founder-accepted with Decision B. Gate 3J implemented and tested
the deterministic clarification foundation only: typed schemas, bounded
taxonomy, state transitions, resolution provenance, edit/remove/dependency
semantics, and confirmation separation. The architecture remains candidate-
only; Gate 4 and Workbench UX remain inactive pending Founder acceptance.

## v0.5.1 Gate 3G — invalidated candidate evidence

- [Gate 3G promotion results](../docs/v0.5.1/gate3g-promotion-results.md)

The one-shot deterministic run completed 180/180, but the frozen benchmark
contained 122 duplicate normalized requests (58 unique rows). The benchmark
quality defect invalidates the apparent perfect metrics; no promotion is made
and no rerun is performed without a new identity and authorization.

## v0.5.1 Gate 3F-R — candidate Result Package

- [Gate 3F-R refinement report](../docs/v0.5.1/gate3fr-stage2-refinement.md)

The deterministic refined arm met the development safety and role targets on
the frozen 36-case prospective fixture. The qwen3:4b arm completed all items
through a resumable harness, but phrase-level role output was malformed and
therefore its comparison is invalid/incomplete. Gate 3F-R is candidate-complete
pending Founder acceptance; Gate 4 remains inactive.

## v0.5.1 Gate 3F — candidate Result Package

- [Gate 3F staged interpretation development](../docs/v0.5.1/gate3f-staged-interpretation-development.md)
- [Gate 3F development fixture](../tests/fixtures/v051_gate3f_development.json)

The six-stage typed baseline and non-executable CandidateInterpretation assembly
were validated on 24 independent development cases. Deterministic role
accuracy was 70.83%, False REQUIRED 0%, False EXCLUDED 0%, CONTEXT_ONLY
accuracy 66.67%, and PREFERRED accuracy 33.33%. The bounded qwen3:4b arm is
implemented but its fixture run was stopped after the local request exceeded the
bounded window; no model quality claim is made. Gate 3F is candidate-complete
pending Founder acceptance; Gate 4 remains inactive.

## v0.5.1 Gate 3F-R — Stage 2 refinement (active)

Gate 3F-R is authorized for one bounded role-classification refinement and a
new prospective development-validation fixture. Gate 3F remains accepted as
development evidence only; Gate 4 remains inactive.

## v0.5.1 Gate 4 — candidate Workbench evidence

The candidate wording in this original package is historical. Gate 4 was later
accepted by the Founder and Gate 5 was separately authorized; see `DECISIONS.md`
D-028/D-029 and the current state record.

- `docs/v0.5.1/gate4-clarification-confirmation-workbench.md` — bounded UI/API
  Result Package and Founder review checklist.
- `src/armie_retrieval/application/workbench.py` and `services/api/app.py` —
  interpretation session and typed resolution/confirmation endpoints.
- `tests/test_v051_gate4_workbench.py` — deterministic lifecycle, API, invalid
  resolution, confirmation, and no-retrieval tests.
- `apps/workbench/tests/workbench.test.js` — clarification UI boundary markers.

Gate 4 is candidate-complete only. It preserves Gate 3J semantics and does not
claim live browser/Elasticsearch acceptance, C1 execution, extractor promotion,
or Gate 5 authorization.

## v0.5.1 Gate 5 — candidate execution-boundary evidence

- `docs/v0.5.1/gate5-confirmed-c1-e2e.md` — architecture, API, safety boundary,
  and Founder Test Script.
- `src/armie_retrieval/application/workbench.py` — deterministic confirmed
  interpretation → canonical RetrievalContract bridge and execution guards.
- `services/api/app.py` — typed execution endpoint bound to session and
  contract fingerprint.
- `tests/test_v051_gate4_workbench.py` — no-confirmation rejection, confirmed
  execution binding, stale contract rejection, and edit invalidation.

Gate 5 remains candidate evidence until live Elasticsearch/browser verification
and Founder acceptance are complete. No Gate 6 or release action is authorized.

The original candidate package recorded focused/full tests and a temporary
local Docker unavailability. That historical limitation was superseded by the
Gate 5-R live runtime verification and the Gate 5-F browser rerun below; it is
not the current execution state.

## v0.5.1 Gate 5-F — candidate Founder integration fix

The bounded Gate 5-F refinement addresses only Founder-observed integration
defects. The backend guard prevents `/query` from bypassing an active
interpretation session; Workbench state is cleared on query/mode changes; the
generic retrieval action is disabled while clarification or confirmation is
active; and the UI reports the backend `blocking_clarification_count`.

Evidence:

- `docs/v0.5.1/gate5-confirmed-c1-e2e.md` — updated Result Package and exact
  Founder case.
- `tests/test_v051_gate4_workbench.py` — 12 focused protocol tests passed,
  including unresolved bypass rejection and confirmed canonical C1 routing.
- `apps/workbench/tests/gate7c.integration.spec.ts` — live Elasticsearch-backed
  browser suite: 10 passed, 0 failed, including the exact
  `around 20 years` → `MINIMUM` → confirm → C1 flow.

This is candidate evidence only. Gate 5 remains unaccepted pending Founder
retest; Gate 6 and release work remain inactive. The controlled synthetic
Dataset v2 and existing C1 semantics are unchanged.

## v0.5.1 Gate 5-F3 — confirmed execution rendering

- [Gate 5-F3 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md)
- `tests/test_v051_gate4_workbench.py` — 17 focused tests, including result
  count/evidence and executed-zero distinctions.
- `apps/workbench/tests/gate7c.integration.spec.ts` — 16 live Elasticsearch-
  backed browser checks, including five-result rendering, valid zero-result
  rendering, confirmed-interpretation invalidation, and new-session reset.

The endpoint already returned the canonical Workbench response. The repair
converges confirmed execution into the same frontend response state used by
manual structured execution. F4 is Founder-verified closed; F6 is validated as
candidate-complete. Gate 5 remains unaccepted and Gate 6 remains inactive.

## v0.5.1 Gate 5-F2 — governed Search and exact Founder-case finding

- [Gate 5-F2 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md)
- `tests/test_v051_gate4_workbench.py` — governed fresh-query blocking,
  confirmation boundary, and canonical C1 routing.
- `apps/workbench/tests/gate7c.integration.spec.ts` — primary Search enters
  interpretation before retrieval, then resolves/ confirms/executes C1.

The confirmed exact Founder query is equivalent to its manual structured
contract and returns zero against the compatible `armie-experts-v0.5-dense`
alias because its physical Gate6B projection contains no `healthcare` values.
Direct counts show 2,307 profiles meeting `years_experience >= 20`, zero
meeting the healthcare predicate, and zero meeting the conjunction; years-only
structured C1 returns results. This is a data/projection finding, not a
semantic retuning or real-world quality claim. Gate 5-F2 is candidate-complete
and awaits Founder retest; Gate 5 remains unaccepted and Gate 6 is inactive.
