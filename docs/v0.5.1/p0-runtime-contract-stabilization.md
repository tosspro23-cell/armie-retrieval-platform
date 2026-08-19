# v0.5.1 Prerequisite Gate P0 — Runtime Identity & Contract Surface Stabilization

**Work Object:** `armie-retrieval-v051-p0-runtime-contract-stabilization`
**Status:** candidate-complete; **READY_FOR_FOUNDER_ACCEPTANCE_TO_START_GATE_0**
is **not yet granted** because raw structured-coverage evidence and a historical
mapping fingerprint remain unresolved prerequisites.
**Scope:** stabilization only; no NL extraction, Gate 0, benchmark generation,
or C1 semantic change.

## 1. Company OS preflight

The repository `AGENTS.md`, `company-os/PROJECT_STATE.md`, and the prior review
Result Package were read before execution. Founder acceptance of the v0.5.1
direction is recorded as conditional on prerequisite stabilization. The P0 Work
Object is bounded by this document and stops before Gate 0.

## 2. Runtime identity boundary

The logical runtime identity is now:

`armie-experts-v0.5-dense`

The preserved physical experiment/build identity is:

`armie-experts-v1-v2-gate6b-dense-10000`

The existing Elasticsearch 8.15.3 environment contains the physical index with
10,000 documents. The logical alias was created atomically over that index; no
reindex or benchmark mutation occurred. Runtime configuration defaults to the
logical identity and still permits an explicit `ARMIE_V050_C1_INDEX` override
for controlled local rebuilds. `ARMIE_V050_C1_PHYSICAL_INDEX` identifies the
current build target for indexing tools.

This is the minimum **alias + explicit configuration** boundary: application
semantics use the logical name, while the physical index can be replaced behind
the alias. The alias is operationally simple, rollback-friendly, testable, and
does not change C1 behavior.

## 3. Compatibility verification

The logical alias resolves to the physical Gate 6B index. Elasticsearch reports
version 8.15.3, green cluster health, and 10,000 documents. Runtime mapping
checks verify projection schema, required fields, embedding model metadata, and
1024 dimensions before a constrained search. An incompatible index returns an
explicit `INDEX_INCOMPATIBLE` result and never silently falls back.

The historical index mapping does not expose the expected mapping fingerprint in
its `_meta`; compatibility therefore reports the observed fingerprint as
unavailable rather than fabricating one. This remains a prerequisite debt item.

## 4. Registry identity and vocabulary

The authoritative registry remains:

`registry_id/version: v0.5-c1-capability-registry-1`
`schema_version: constraint-registry-v1`

It exposes supported fields (`years_experience`, `industry`, `role`,
`location`, `seniority`), operators, deferred categories, canonical categorical
values, and display labels separately. For example, canonical
`financial services` is displayed as `Financial Services`; model output in a
future version must target canonical values, not labels.

Evolution policy:

- PATCH: display aliases or metadata only; canonical semantics unchanged.
- MINOR: a newly supported deterministic field/operator with an explicit
  registry version.
- BREAKING: changing canonical value meaning or operator semantics.

## 5. Execution provenance contract

The stabilized execution provenance identity is:

`constraint-execution-provenance-v1`

Stable product/API fields include requested K, candidate-pool count, eligible
count, returned K, shortfall, contract state, strategy/runtime identity,
logical/resolved index identity, projection identity, registry identity,
constraint traces, exclusions, structured candidate facts, and compatibility
status. ANN settings and latency stages remain diagnostic fields.

Additive optional diagnostics are backward compatible. Changing the meaning or
removing a stable field requires a new provenance schema identity. Future
interpretation provenance (`NL → candidate contract`) must be separate from
execution provenance (`validated contract → C1 retrieval`) and is not
implemented in P0.

## 6. Structured-data coverage audit

The repository does not contain the raw 10,000-profile corpus, so exact
prevalence distributions cannot be independently recomputed in P0 without
regenerating or importing an artifact. The carried-forward audit confirms:

| Field | Current evidence |
|---|---|
| `years_experience` | schema/semantics verified; prevalence not measurable here |
| `seniority` | closed enum `mid`, `senior`, `principal`; prevalence not measurable here |
| `industry` | canonical field/provenance semantics verified; prevalence not measurable here |
| `role` | aggregate and relationship-specific semantics verified; prevalence not measurable here |
| `location` | projection field present; prevalence not measurable here |

The previously observed Healthcare gap remains explicit: the Gate 6B indexed
projection is populated with Financial Services and Manufacturing examples but
does not provide an independently verified Healthcare-positive distribution.
Registry presence is not corpus coverage.

## 7. v0.5.1 data-extension plan

No data was generated or mutated. A future, newly identified extension must
preserve lineage to `v2-realism-full` and its immutable checksum
`514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`.

The extension should be a separately versioned deterministic synthetic
augmentation or dedicated evaluation fixture with positive/negative coverage
for Healthcare and other industries, seniority bands, numeric thresholds,
roles, locations, exclusions, and conjunctions. It must produce two distinct
layers:

1. extraction benchmark data: natural language → expected candidate contract;
2. retrieval corpus/projection data: valid contract → eligible candidates.

An end-to-end benchmark must not collapse these layers into one metric.

## 8. API and behavior compatibility

Capabilities and `/api/v1/constraints/registry` expose registry identity,
schema version, supported fields/operators, canonical values, and display
labels. Structured-query responses expose the execution provenance schema
identity and existing C1 evidence fields.

The runtime contract remains unchanged:

- no contract → C0 H2 Dense;
- valid supported contract → C1 native pre-filter + H2 Dense;
- unsupported contract → explicit unsupported state;
- invalid contract → explicit invalid state;
- incompatible index → explicit compatibility failure.

No relaxation, fallback, or Gate 6D metric semantics were changed.

## 9. Validation result

- Alias resolution: passed; logical alias resolves to the preserved physical
  index and count is 10,000.
- Elasticsearch: passed; 8.15.3, green cluster.
- Mapping compatibility: passed for schema/fields/dimensions; fingerprint
  metadata is unavailable on the historical index and remains a blocker.
- Live C0 smoke: 5/5 unfiltered Dense results returned through the logical
  boundary.
- Live C1 smoke: years and populated Manufacturing constraints returned 5/5
  eligible results; explicit Financial Services exclusion returned 5/5.
- Live strict-shortfall smoke: Healthcare returned 0/5 with explicit strict
  shortfall under the known coverage gap.
- Targeted P0 tests: added for logical identity, alias resolution, registry
  identity/labels, and provenance identity.
- Full Python suite: 135 passed, 3 skipped; the skips are opt-in Elasticsearch
  or Gate 4 integration tests when their explicit environment flag is absent.
- Elasticsearch-enabled compatibility/integration subset: 12 passed.
- Frontend unit tests: 5 passed; production build passed.
- Workbench browser smoke: not run because no backend/frontend services were
  started for P0; direct C0/C1 Elasticsearch smoke covered runtime behavior.
- Markdown links: validated after documentation completion.
- `git diff --check`: required before completion.

## 10. Prerequisite disposition and Gate 0 entry contract

| Prerequisite | Disposition |
|---|---|
| Stable logical index identity | CLOSED, with historical fingerprint follow-up |
| Registry identity/versioning | CLOSED for P0 |
| Provenance schema identity/rules | CLOSED for P0 |
| Structured data coverage | REMAINS BLOCKING until raw field-profile evidence exists |
| v0.5.1 data-extension plan | READY, but not materialized |

Gate 0 may assume stable logical identity, explicit registry vocabulary,
`constraint-execution-provenance-v1`, immutable v0.5.0 lineage, and an approved
data-extension plan. Gate 0 may not begin until the founder accepts this P0
Result Package and the coverage/fingerprint blockers are resolved or explicitly
waived.

## Stop condition

P0 stops here. No NL extraction, HARD/SOFT interpretation, benchmark
generation, Gate 0, v0.6 work, commit, tag, or push was started.
