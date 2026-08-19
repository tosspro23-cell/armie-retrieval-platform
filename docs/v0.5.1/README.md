# ARMIE Retrieval Platform v0.5.1

This directory contains the v0.5.1 prerequisite, interpretation, Workbench,
and confirmed-interpretation → C1 evidence.

## Release-stabilization status

Gate 5 and its bounded F/F2/F3 fixes are Founder-accepted. The v0.5.1
capability boundary is frozen and release stabilization is active. The release
is not yet committed, tagged, pushed, or represented by a GitHub Release
object; the [Company OS](../../company-os/PROJECT_STATE.md) remains the
authoritative mutable state record.

- [Release notes](release-notes.md)
- [Gate 5 Result Package](gate5-confirmed-c1-e2e.md)
- [Release Start Gate](../../company-os/V051_RELEASE_START_GATE.md)

- [P0 runtime identity and contract stabilization](p0-runtime-contract-stabilization.md)
- [Gate 0 governed natural-language contract charter](gate0-nl-contract-charter.md)
- [Gate 1 interpretation and benchmark foundation](gate1-interpretation-benchmark-design.md)
- [Gate 2 extraction baseline comparison](gate2-extraction-baseline-comparison.md)
- [Gate 3 frozen extraction evaluation](gate3-frozen-extraction-evaluation.md)
- [Gate 3 evaluation manifest](gate3-evaluation-manifest.json)
- [Gate 3B model coverage closure](gate3b-model-coverage.md)
- [Gate 3B coverage results](gate3b-coverage-results.json)
- [Gate 3C resumable evaluation](gate3c-resumable-evaluation.md)
- [Gate 3C result summary](gate3c-evaluation-results.json)
- [Gate 2 comparison result artifact](gate2-comparison-results.json)

The v0.5.0 dataset, benchmark, projection lineage, and Gate 6D results remain
immutable historical release evidence. Gate 0, Gate 1, and experimental Gate 2
are accepted; Gate 3J, Gate 4, and Gate 5 are accepted with no extractor
promotion. See the local Company OS records for authoritative state, evidence
layers, and acceptance boundaries.

## Gate 3C status

The checkpointed harness completed both qwen3:4b model and hybrid arms over all
120 frozen items (120/120 terminal each, no infrastructure or structured-output
failures). The model arm fails the frozen semantic thresholds (exact 0%,
precision 30%, recall 30%, unsupported preservation 80%); hybrid reproduces the
rule-authoritative profile and also fails. Gate 3 is candidate-complete and
READY_FOR_FOUNDER_ACCEPTANCE for the semantic promotion decision. Gate 4 remains
inactive.

## v0.5.1 Gate 3D — semantic refinement

- [Gate 3D semantic refinement Result Package](gate3d-semantics-refinement.md)
- [Gate 3D machine result](gate3d-evaluation-results.json)

Gate 3C execution evidence was accepted by the founder with architecture
promotion decision D (no promotion). Gate 3D was explicitly authorized to
refine interpretation semantics. Rule v3, Model v2, and Cascade v2 completed
the unchanged 120-item benchmark, but all remain below frozen promotion
thresholds. Gate 4 remains inactive.

## Gate 3E — architecture reassessment

[Gate 3E failure decomposition and architecture reassessment](gate3e-architecture-reassessment.md)
was accepted by the Founder as the Path A architecture direction. It remains
evidence/design work only: no extractor was promoted, no benchmark or
threshold was changed, and Gate 4 remains inactive.

## Gate 3F — staged interpretation

Gate 3F is authorized for development-only staged interpretation design and
validation. The six stage boundaries, role ontology, explicit-requirement-only
safety boundary, and separate development fixture are governed by the active
Company OS Work Object. Gate 4 remains inactive and no extractor is promoted.

- [Gate 3F staged interpretation development Result Package](gate3f-staged-interpretation-development.md)

- [Gate 3F-R Stage 2 refinement Result Package](gate3fr-stage2-refinement.md)

- [Gate 3G promotion results](gate3g-promotion-results.md)
- [Gate 3G-R promotion contract v2](gate3gr-promotion-contract-v2.md)
- [Gate 3G-R promotion results](gate3gr-promotion-results.md)
- [Gate 3H model capability results](gate3h-model-capability-results.md)
- [Gate 3I role-only results](gate3i-role-only-results.md)
- [Gate 3J clarification protocol](gate3j-clarification-protocol.md)
- [Gate 4 clarification and confirmation Workbench](gate4-clarification-confirmation-workbench.md)
- [Gate 5 confirmed interpretation to C1](gate5-confirmed-c1-e2e.md)
