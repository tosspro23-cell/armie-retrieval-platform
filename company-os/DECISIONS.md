# ARMIE Company OS Decisions

## Accepted decisions

### D-001 — Manual state protocol

Company OS v0.1 is a manual, state-governed protocol using versioned local
project files. It is not a Python runtime or UI. Chats support reasoning; Git
is code truth. Evidence is required for proposed transitions and the founder
owns consequential decisions.

**Revisit when:** the founder explicitly authorizes a different operating model.

### D-002 — Retrieval Platform as first validation project

The Retrieval Platform is the first project used to validate the Company OS
protocol.

**Revisit when:** the founder adds or changes the validation portfolio.

### D-003 — Dataset v1 immutability

Dataset v1 remains the immutable controlled synthetic regression baseline.

**Revisit when:** a versioned replacement is accepted through a separate,
evidence-backed decision; never by silently rewriting v1.

### D-004 — Gate 5.5A accepted; v1 remains immutable

Gate 5.5A was accepted and committed at `57a1be9`. Dataset v1 remains the
immutable controlled synthetic regression baseline.

**Revisit when:** a separately evidenced versioned dataset decision is accepted.

### D-005 — Gate 5.5B benchmark checkpoint completed

Gate 5.5B benchmark and stability analysis were completed and checkpointed in
`58baad4` and `9973367`. The results remain controlled synthetic evidence and
must not be generalized to natural expert-network quality.

**Revisit when:** a future evidence-backed benchmark phase is explicitly
authorized.

### D-006 — Gate 6 accepted and committed

The founder accepted the Gate 6 Workbench Acceptance / Relevance Experiment UX
Result Package. It is committed at `5ee33a1b098c20a313fe04603e371e2fc4768ee6`
with 17 Chromium acceptance checks and preserved runtime semantics.

**Revisit when:** a future Workbench revision is explicitly authorized.

### D-007 — v0.4.0 release accepted and pushed

The founder accepted Gate 7 and the v0.4.0 release. Release commit
`266bf5b8c4a81aee30231d486312b03c4eca96db` is on `origin/main`; annotated tag
`v0.4.0` is pushed and peels to that commit. GitHub Release-object lookup was
verified as absent (HTTP 404). A tag and a GitHub Release object remain
distinct states.

**Revisit when:** a future release or an explicitly authorized GitHub Release
object decision is made.

## Accepted release state

Gate 6, Gate 7 and the v0.5.0 Gate 9 release are accepted and written back.
The v0.5.0 tag is immutable at its validated release commit; the current
branch head may advance with closeout documentation. Any future release
requires a new founder decision and a new Result Package with remote-reference
verification.

## v0.5.0 release decision

### D-009 — v0.5.0 released and accepted

The founder accepted the v0.5.0 engineering/Git release. C0 remains the
unconstrained H2 Dense baseline; C1 is promoted for supported structured hard
constraints; C2 is diagnostic/de-prioritized; C3 is deferred. The release is
limited to deterministic structured constraints and does not include
NL-to-RetrievalContract extraction, general temporal/relationship/evidence
semantics, or production C2/C3.

Release commit `05e661f` is the annotated `v0.5.0` tag target, tag object
`b4230aee`; final `main` and `origin/main` are `f181960`. No GitHub Release
object was created or independently verified.

**Revisit when:** a post-release architecture review accepts a new version or
release scope.

## Proposed next direction

Natural Language → RetrievalContract is a proposed v0.5.1 direction only,
pending post-release architecture review. It is not active implementation.

### D-010 — Post-release review recommendation

The bounded v0.5.0 post-release review recommends v0.5.1 Governed Natural
Language → RetrievalContract, subject to prerequisite debt closure and explicit
founder acceptance. The proposed layer must produce a candidate contract,
require user confirmation, and pass the existing deterministic validator before
existing C1 execution. This is `READY_FOR_FOUNDER_ACCEPTANCE`, not an accepted
version-scope decision or active implementation.

**Evidence:** `docs/v0.5.0/post-release-architecture-review.md`.

**Revisit when:** the founder accepts/rejects the proposed v0.5.1 boundary or
authorizes a different next-version direction.

### D-011 — v0.5.1 direction conditionally accepted; P0 required

The founder conditionally accepted the proposed v0.5.1 direction and then
authorized Gate 0 with P0 accepted-with-carry-forward conditions. The bounded
P0 stabilization records a logical dense-index identity, registry versioning,
execution provenance identity, and a data-extension plan without implementing
NL extraction. Gate 0 is limited to architecture/specification work and awaits
founder acceptance of its charter; Gate 1 remains inactive.

**Evidence:** `docs/v0.5.1/p0-runtime-contract-stabilization.md`.

**Revisit when:** the founder accepts/rejects P0 or changes the v0.5.1 scope.

### D-012 — Gate 0 charter authorized; candidate acceptance pending

**Historical disposition:** superseded by D-013 after the founder accepted the
Gate 0 charter and authorized Gate 1.

The founder authorized v0.5.1 Gate 0 after accepting P0 with carry-forward
conditions. Gate 0 freezes the bounded Governed Natural Language → candidate
`RetrievalContract` architecture, conservative HARD/SOFT/unsupported semantics,
mandatory confirmation, deterministic validation boundary, interpretation
provenance boundary, safety metrics, annotation model, and Gate 1 entry
contract. It does not implement extraction, call a model, generate benchmark
instances, change C1, or start Gate 1.

**Evidence:** `docs/v0.5.1/gate0-nl-contract-charter.md`.

**Disposition:** `READY_FOR_FOUNDER_ACCEPTANCE`; Gate 1 remains inactive.

**Revisit when:** the founder accepts/rejects the Gate 0 charter or authorizes a
different v0.5.1 scope.

### D-013 — Gate 0 accepted; Gate 1 authorized

The founder accepted the Gate 0 charter and authorized Gate 1. Gate 1 is
limited to the versioned candidate-interpretation schema, gold annotation and
benchmark foundation, deterministic evaluator, and hand-audited fixture. It
does not implement extraction, call models, change C1, or start Gate 2.

**Evidence:** `docs/v0.5.1/gate1-interpretation-benchmark-design.md`.

**Revisit when:** the founder accepts/rejects the Gate 1 Result Package or
authorizes a different v0.5.1 scope.

### D-014 — Gate 1 accepted; Gate 2 authorized

The founder accepted Gate 1 and authorized Gate 2. Gate 2 is limited to
bounded rule, structured Ollama, and conservative hybrid CandidateInterpretation
baselines, a frozen development fixture, deterministic comparison, and
failure analysis. No arm is promoted to production architecture; Gate 3,
Workbench integration, and C1 execution remain inactive.

**Evidence:** `docs/v0.5.1/gate2-extraction-baseline-comparison.md`.

**Revisit when:** the founder accepts/rejects the Gate 2 Result Package or
authorizes Gate 3.

### D-015 — Gate 2 experimental acceptance; Gate 3 authorized

The founder accepted Gate 2 as an experimental result with Outcome E
(insufficient evidence for architecture promotion) and authorized Gate 3 as a
frozen evaluation and safety promotion study. No extractor is promoted and
Gate 4 remains inactive.

**Evidence:** Founder-provided Gate 3 authorization and
`docs/v0.5.1/gate2-extraction-baseline-comparison.md`.

**Revisit when:** the Gate 3 Result Package is complete and the founder
accepts/rejects its candidate-only promotion recommendation.

### D-016 — Gate 3C execution coverage closed; semantic acceptance pending

Gate 3C repaired the evaluation harness without changing the frozen benchmark,
prompt, schema, labels, or thresholds. qwen3:4b model and hybrid arms completed
120/120 terminal items with durable checkpoints and valid run integrity, but both
arms fail the frozen semantic promotion thresholds. Gate 3 is candidate-complete
and READY_FOR_FOUNDER_ACCEPTANCE; no extractor is promoted and Gate 4 remains
inactive.

**Evidence:** `docs/v0.5.1/gate3c-resumable-evaluation.md` and
`docs/v0.5.1/gate3c-evaluation-results.json`.

**Revisit when:** the founder accepts/rejects the semantic Result Package and,
if accepted, separately authorizes Gate 4.

### D-017 — Gate 3C accepted; Gate 3D authorized; no architecture promotion

The founder accepted the Gate 3C execution Result Package, closed its
infrastructure work, selected architecture decision D (no extractor promotion),
and authorized Gate 3D semantic refinement. Gate 4 remains inactive.

**Evidence:** Founder-provided Gate 3D authorization, `docs/v0.5.1/gate3c-resumable-evaluation.md`,
and `docs/v0.5.1/gate3d-semantics-refinement.md`.

**Revisit when:** Gate 3D semantic Result Package is accepted/rejected by the
founder; no promotion may be inferred from candidate evidence.

### D-018 — Gate 3D accepted; Gate 3E architecture review authorized

The founder accepted the Gate 3D semantic Result Package and retained
architecture decision D (no extractor promotion). Gate 3E was authorized as a
bounded failure-decomposition and architecture-reassessment review. It
produced a candidate staged-interpretation recommendation without changing
code, prompts, benchmark identity, thresholds, models, runtime, C1, Workbench,
or Gate 4 status.

**Evidence:** [Gate 3E reassessment](../docs/v0.5.1/gate3e-architecture-reassessment.md).

**Revisit when:** the founder accepts/rejects Gate 3E and, if accepted,
separately authorizes a future Gate 3F or Gate 4.

### D-019 — Gate 3E accepted; Gate 3F authorized

The founder accepted Gate 3E and authorized Gate 3F to design and validate a
staged interpretation baseline on development-only evidence. The staged
architecture remains candidate-only; explicit-requirement-only remains the
interim safety boundary. Gate 4, C1, Workbench, frozen-120 tuning, stronger
models, and extractor promotion remain out of scope.

**Evidence:** Founder-provided Gate 3F authorization and the Gate 3F Work
Object in `company-os/CURRENT_WORK.md`.

**Revisit when:** Gate 3F Result Package is ready for Founder acceptance.

### D-020 — Gate 3F accepted as development evidence; Gate 3F-R authorized

The founder accepted Gate 3F as development evidence, retained the staged
architecture as promising but unpromoted, and authorized exactly one bounded
Stage 2 role-classification refinement. Gate 4 remains inactive; no stronger
model, C1, Workbench, or frozen-120 tuning is authorized.

**Evidence:** Founder-provided Gate 3F-R authorization and the active Work
Object in `company-os/CURRENT_WORK.md`.

### D-021 — Gate 3F-R candidate completion

The deterministic Stage 2 refinement met the bounded development safety and
role targets on the new 36-case fixture. The qwen3:4b comparison completed
coverage through a resumable harness but produced malformed phrase-level role
output, so the model comparison is invalid/incomplete. Gate 3F-R is
READY_FOR_FOUNDER_ACCEPTANCE; Gate 4 remains inactive.

**Evidence:** [Gate 3F-R report](../docs/v0.5.1/gate3fr-stage2-refinement.md).

### D-022 — Gate 3G evidence invalidated; no promotion

The deterministic staged candidate completed the single Gate 3G run, but the
180-item benchmark contained 122 duplicate normalized requests. The apparent
perfect metrics are invalid evidence. No extractor is promoted and Gate 4
remains inactive. Any repaired benchmark requires a new identity and explicit
authorization.

**Evidence:** [Gate 3G results](../docs/v0.5.1/gate3g-promotion-results.md).

### D-023 — Gate 3G evidence invalid; no promotion

Gate 3G was authorized to create and execute a new prospective promotion
benchmark. Its single deterministic run is invalidated because 122 of 180
normalized requests were duplicates. No promotion or Gate 4 authorization is
implied; a repaired benchmark requires a new identity and Founder direction.

### D-024 — Gate 3G-R valid evidence; candidate not promoted

The new prospective benchmark passed its admission gates and the deterministic
candidate executed exactly once. The candidate failed the frozen role, safety,
mapping, and unsupported-preservation thresholds (Decision B). This candidate
disposition is pending Founder acceptance; Gate 4 remains inactive.

**Evidence:** [Gate 3G-R results](../docs/v0.5.1/gate3gr-promotion-results.md).

**Revisit when:** the Founder accepts or rejects the Result Package and, if
desired, separately authorizes a successor gate.

### D-025 — Gate 3H model capability study; no model-assisted candidate

The Founder accepted Gate 3G-R Decision B and authorized Gate 3H. On the
development-only fixture, qwen3:4b remained phrase-contract invalid and qwen3:8b
produced token-level spans with unsafe False REQUIRED/EXCLUDED rates. Decision C
is proposed: retain deterministic staged interpretation and do not create a
model-assisted candidate. Gate 4 remains inactive pending Founder acceptance.

**Evidence:** [Gate 3H results](../docs/v0.5.1/gate3h-model-capability-results.md).

### D-026 — Gate 3I role-only model study; insufficient for promotion

The Founder accepted Gate 3H Decision C and authorized Gate 3I. Deterministic
Stage 1 produced stable candidate spans and qwen3:8b role-only output was
schema-valid with a real lift over Gate 3H, but False REQUIRED was 32.79% and
context/unsupported/ambiguous distinctions remained unsafe. Decision B is
proposed; no model-assisted candidate or Gate 4 work is authorized.

**Evidence:** [Gate 3I results](../docs/v0.5.1/gate3i-role-only-results.md).

### D-027 — Gate 3J clarification architecture candidate

The Founder accepted Gate 3I Decision B and authorized Gate 3J. The bounded
protocol introduces typed clarification items/resolutions, deterministic
resolution application, blocking-vs-non-blocking policy, confirmation
separation, provenance, edit/remove/dependency semantics, and a no-clarification
fast path. Uncertainty must flow to clarification rather than autonomous
hardening. This architecture is candidate-only pending Founder acceptance.

**Evidence:** [Gate 3J protocol](../docs/v0.5.1/gate3j-clarification-protocol.md).

### D-020 — Gate 3F accepted as development evidence; Gate 3F-R authorized

The founder accepted the Gate 3F Result Package as development evidence,
retained the staged architecture as promising but unpromoted, and authorized
exactly one bounded Stage 2 role-classification refinement. Gate 4 remains
inactive; no stronger model, C1, Workbench, or frozen-120 tuning is authorized.

**Evidence:** Founder-provided Gate 3F-R authorization and the active Work
Object in `company-os/CURRENT_WORK.md`.

### D-028 — Gate 4 clarification/confirmation Workbench candidate

The founder accepted Gate 3J and Clarification Protocol v1 and authorized Gate
4. Gate 4 connects the protocol to a structured Workbench review and typed API,
retaining mandatory confirmation and stopping at `VALIDATED_CONTRACT`. It does
not execute C1, promote an extractor, add conversational UI, or authorize Gate
5. The Gate 4 Result Package is candidate-complete and awaits Founder
acceptance.

**Evidence:** `docs/v0.5.1/gate4-clarification-confirmation-workbench.md`.

**Revisit when:** the Founder accepts/rejects Gate 4 or authorizes a different
Workbench/interpretation scope.

### D-029 — Gate 5 confirmed interpretation to C1 authorized

The founder accepted Gate 4 and authorized Gate 5. Gate 5 may connect only a
`VALIDATED_CONTRACT` produced by explicit confirmation to the existing
v0.5.0 C1 validator/compiler/native Elasticsearch path. Unconfirmed,
unsupported, stale, or edited interpretations must not execute. Gate 5 is
active and pending runtime/browser evidence and Founder acceptance; Gate 6 and
release work remain inactive.

**Evidence:** `docs/v0.5.1/gate5-confirmed-c1-e2e.md`.

**Revisit when:** the Founder accepts/rejects Gate 5 or changes the execution
boundary.

### D-030 — Gate 5-F bounded Founder integration fix (candidate)

Founder testing exposed three Workbench integration defects: the generic query
path could bypass an active interpretation session, the clarification status
could misstate blocking work, and the review/action hierarchy was unclear. The
bounded Gate 5-F fix routes active sessions through canonical governed
execution, exposes the backend blocking count, disables the generic action
during review, and preserves clarify → confirm → execute. It does not alter
interpretation semantics, C1 behavior, Dataset v2, or Gate 6 authorization.

**Evidence:** `docs/v0.5.1/gate5-confirmed-c1-e2e.md`,
`tests/test_v051_gate4_workbench.py`, and
`apps/workbench/tests/gate7c.integration.spec.ts` (10/10 live).

**Disposition:** candidate-complete / READY_FOR_FOUNDER_RETEST; not accepted.

**Revisit when:** the Founder retests and accepts/rejects Gate 5-F.

### D-031 — Gate 5-F2 governed Search boundary and F5 data finding (candidate)

Gate 5-F2 adds only the missing integration boundary: primary Search in
governed C1 mode must enter interpretation first, block fresh execution, and
require explicit confirmation before canonical C1 execution. The exact Founder
query is contract-equivalent between confirmed natural language and manual
structured execution. Its zero result is explained by the current compatible
projection containing no `healthcare` industry values (years-only returns
results); no semantic retuning is approved or implied.

**Evidence:** [Gate 5-F2 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md),
`tests/test_v051_gate4_workbench.py`, and
`apps/workbench/tests/gate7c.integration.spec.ts`.

**Disposition:** candidate-complete / READY_FOR_FOUNDER_RETEST_2; Gate 5 remains
unaccepted and Gate 6 remains inactive.

**Revisit when:** the Founder retests the primary Search flow and reviews the
explicit F5 index/data limitation.

### D-032 — Gate 5-F3 confirmed result rendering (candidate)

F4 governed Search is Founder-verified closed. F6 was a frontend/application
state divergence: confirmed execution populated only the interpretation panel's
local status, while manual structured execution populated the canonical
Workbench response consumed by Answer Summary, Results, Audit, Evidence,
Metrics, and Execution Context. The bounded repair forwards the existing
confirmed `WorkbenchResponse` into that canonical state without changing the
API schema, retrieval semantics, C1, or Dataset v2. Positive result counts and
valid zero-result responses are both rendered distinctly from no execution.

**Evidence:** [Gate 5-F3 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md),
`tests/test_v051_gate4_workbench.py`, and
`apps/workbench/tests/gate7c.integration.spec.ts` (16/16 live, including the
Founder-critical result-state invalidation and new-session reset paths).

**Disposition:** candidate-complete / READY_FOR_FOUNDER_RETEST_3; Gate 5 remains
unaccepted and Gate 6 remains inactive.

**Revisit when:** the Founder retests five-result and zero-result confirmed
execution rendering and accepts/rejects the Result Package.

### D-033 — Company OS record synchronization controls

The Founder authorized a governance-only remediation after the 2026-08-17
audit. The project must maintain exactly one active Work Object, a separately
linkable Task Contract/Start Gate for each material gate, explicit historical
supersession markers, evidence-layer classification, and a repeatable
pre-review consistency check. This decision does not accept Gate 5-F3, start
Gate 6, or alter product/runtime state.

**Evidence:** `company-os/GOVERNANCE_AUDIT_2026-08-17.md`,
`company-os/GATE5_F3_START_GATE.md`, and
`scripts/check_company_os_consistency.py`.

**Revisit when:** the Founder changes the Company OS operating protocol or
authorizes a successor governance revision.

### D-034 — Gate 5 closure and v0.5.1 release authorization

The Founder accepted Gate 5, including the bounded Gate 5-F, Gate 5-F2, and
Gate 5-F3 fixes, froze the v0.5.1 capability boundary, and authorized release,
GitHub publication, and closeout. The historical candidate dispositions in
D-030 through D-032 describe the state at capture and are superseded only for
acceptance status; their evidence and scope boundaries remain intact.

The release remains limited to governed natural-language interpretation,
bounded clarification/resolution, explicit confirmation, and execution through
the pre-existing deterministic C1 substrate. It does not authorize v0.6 or any
new capability.

**Evidence:** `docs/v0.5.1/gate5-confirmed-c1-e2e.md`,
`company-os/V051_RELEASE_START_GATE.md`, and the Founder release authorization.

**Revisit when:** post-push reconciliation records the immutable v0.5.1 release
identity and closes the release Work Object.

### D-035 — v0.5.1 release closeout

The authorized v0.5.1 release completed its bounded validation, Git, remote,
tag, and GitHub Release operations. Release commit
`c4bf57fd4ead76cdc18a36e885eea9a5215401a4` was pushed on `main` and remains
reachable from `origin/main`.
Annotated tag `v0.5.1` has object
`6ef90af0b76add2186cd31ef0d74150665234bf8` and peels to `c4bf57f`. The GitHub
Release object is published at
https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1.

This closes the release Work Object. It does not authorize v0.6, any new
capability, C1 semantic change, Dataset v2 change, or benchmark change.

**Evidence:** `company-os/CURRENT_WORK.md`,
`company-os/V051_RELEASE_START_GATE.md`,
`docs/v0.5.1/release-notes.md`, verified `git ls-remote origin`, and the
published GitHub Release object.

**Revisit when:** the Founder explicitly authorizes a successor Work Object.

### D-036 — CI Revival 2026-08 accepted and merged

The Founder (repo owner) reviewed PR #1
(https://github.com/tosspro23-cell/armie-retrieval-platform/pull/1) in this
session and explicitly authorized both this Company OS write-back and
merging the branch into `main` with a regular merge commit. This acceptance
is recorded because the Founder gave it directly in this dispatch — it is
not inferred from CI passing or from prior agent execution.

The Work Object (`ci-revival-2026-08`) restored a passing GitHub Actions CI
baseline using only test-harness and CI-configuration changes: no change to
`src/armie_retrieval/`, `services/`, or any retrieval/planning/ranking/C1
behavior. Four independently-verified root causes were fixed in commit
`02a816a`; a Python-3.9-only dependency gap (`eval_type_backport`, `httpx`)
surfaced once the 3.11 leg started passing was fixed in `05a6f8e`; and a
Codex automated-review finding about a test that could silently no-op-pass
was fixed in `edb80ee`. A second Codex finding, requesting this Company OS
backfill be bundled into the CI-fix commits themselves, was declined as
out of the spec's declared scope and completed instead as this separate,
explicit, Founder-authorized step.

**Evidence:** `company-os/CURRENT_WORK.md` (`ci-revival-2026-08`), PR #1 and
its commits, and the passing CI runs recorded there for both the `3.9` and
`3.11` matrix legs.

**Revisit when:** the Founder authorizes a successor Work Object, or CI
regresses again requiring a further fix.

### D-037 — GOV-CONV-001 governance-interface sample accepted

The Founder accepted the bounded Retrieval governance-interface Result Package
on 2026-08-30 and authorized its Company OS write-back, repository commit, and
GitHub push. The accepted scope is limited to a source-pointed Governance
Surface, local adapter and agent-entry guidance, and consistency validation.
It does not change retrieval behavior, CI workflows, release identity, or
authorize v0.6.

The governance surface is a read model that points to engineering, CI, Project
OS, and release truth; it is not a second GitHub/CI ledger. Future executable
Work Objects must name their traceability matrix, no-model smoke, and relevant
Unit/Integration/Live evidence. This governance-only Work Object makes no
retroactive capability-readiness claim.

The accepted repository branch remains distinct from canonical `main` until it
is merged. Until then, normal main-branch dispatches must treat this as an
accepted alignment candidate rather than claim the local governance interface
is already present on `main`.

**Evidence:** `company-os/GOVERNANCE_CONVERGENCE_PHASE1_START_GATE.md`,
`company-os/GOVERNANCE_CONVERGENCE_PHASE1_RESULT_PACKAGE.md`,
`company-os/GOVERNANCE_SURFACE.md`, `AGENTS.md`, and
`scripts/check_company_os_consistency.py`.

**Revisit when:** the branch is merged into the canonical repository branch,
or the next material executable Work Object exposes a schema or control gap.
