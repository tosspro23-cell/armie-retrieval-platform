# Gate 3F-R — Stage 2 Role Classification Refinement

**Status:** Candidate-complete; READY_FOR_FOUNDER_ACCEPTANCE
**Verdict:** **E — Evidence invalid/incomplete for the model-assisted arm.**
**Scope:** One bounded Stage 2 refinement only. Gate 3F is accepted as
development evidence; Gate 4 remains inactive. The frozen 120-item benchmark
was not run or changed.

## Preflight and boundaries

The active Work Object is `armie-retrieval-v051-gate3fr-stage2-refinement`.
The architecture remains six staged components. Stage 2 receives a detected
span plus the smallest surrounding request context needed for scope; it does
not map registry values, normalize operators, or assemble executable contracts.
No C1, Workbench, RetrievalContract, stronger model, promotion benchmark,
commit, tag, or push was performed.

## Stage 2 error taxonomy from the 24-case reference fixture

The original 24-case fixture is tuning/development evidence only. Its observed
misses were:

| Class | Count | Representative cause |
|---|---:|---|
| A PREFERRED → AMBIGUOUS | 0 | refined preference cues are explicit |
| B PREFERRED → CONTEXT_ONLY | 0 | preference cues preserved |
| C CONTEXT_ONLY → AMBIGUOUS | 0 | context is classified conservatively |
| D CONTEXT_ONLY → REQUIRED | 0 | no registry-only hardening observed |
| E REQUIRED → AMBIGUOUS | 0 | explicit requirement cues preserved |
| F exclusion polarity/scope | 0 | exclusion cues remain EXCLUDED |
| G unsupported confusion | 0 | relationship/temporal items remain UNSUPPORTED |
| H span-boundary | 1 | combined “healthcare context” phrase was too narrow |
| I other | 0 | — |

The refinement was principled rather than sentence-specific: preserve
preference/scope cues, recognize suffix requirement cues, and broaden Stage 1
only when necessary to provide Stage 2 enough context.

## Refined truth conditions

`REQUIRED` means an explicit eligibility condition; `EXCLUDED` means an explicit
disqualifier; `PREFERRED` means desired but non-mandatory; `CONTEXT_ONLY` is
descriptive background; `UNSUPPORTED` is explicit but outside current C1
semantics; `AMBIGUOUS` is genuine unresolved intent. Registry-value presence
alone never determines role. “Must have experience working with Healthcare
teams” can be REQUIRED as an experience proposition without implying
`industry=healthcare`.

## Identities and fixture

- Refined deterministic Stage 2: `deterministic-staged-v2-gate3fr` (implemented
  within the existing `staged-interpretation-v1` downstream contract).
- Model-assisted Stage 2: `staged-qwen3-4b-span-role-v1`, prompt
  `gate3f-span-role-v1`.
- Prospective fixture: `v0.5.1-gate3fr-staged-dev-validation-v1`, **36 items**,
  SHA-256 `9273b08c4390ecc8385286f5237165599d85d4110c1616397866494ff12ec78e`.
  Labels were frozen before the final comparison and were not edited after
  observing results.

## Frozen development targets

Targets were fixed before comparison: False REQUIRED 0%, False EXCLUDED 0%,
semantic-only False REQUIRED 0%, role accuracy ≥85%, CONTEXT_ONLY ≥80%,
PREFERRED ≥80%, and mapping/value/operator correctness ≥95% on correctly
classified supported spans. These are development targets, not promotion
thresholds.

## Deterministic refined arm

On the 36-case validation fixture:

- role accuracy: **86.49%** (32/37 annotated role assertions);
- False REQUIRED: **0%**;
- False EXCLUDED: **0%**;
- CONTEXT_ONLY accuracy: **100%**;
- PREFERRED accuracy: **85.71%**;
- supported registry mapping: **100%** on correctly classified supported spans;
- operator normalization: **100%** on correctly classified numeric spans;
- mean/p50/p95 latency: **0.113 / 0.051 / 0.121 ms**.

Compared with the original Gate 3F development result (70.83% role accuracy,
66.67% CONTEXT_ONLY, 33.33% PREFERRED), the refinement improves generalization
without sacrificing either safety metric. The old and new fixtures are not
treated as interchangeable benchmark populations.

## Model-assisted arm

The resumable harness completed **36/36** items, with **34 model calls** and 2
explicit deterministic fallbacks. Mean/p50/p95 latency was approximately
**2500 / 2169 / 4781 ms**. The qwen output was not semantically usable for this
comparison: it frequently returned token-level spans and prompt-contaminated
role objects rather than the requested phrase-level spans. Exact phrase-role
alignment was therefore **0%** and no quality claim is made. This is a bounded
structured-output/prompt-contract failure, not evidence that qwen is incapable
of the task. Downstream deterministic stages remained intact.

## First-failing-stage distribution

For the deterministic validation arm, remaining misses are Stage 1/2 span-role
boundary cases; no Stage 3 mapping or Stage 4 normalization failure was
observed on correctly classified supported spans. For the model arm, malformed
phrase spans make Stage 1/2 the first failing boundary. No cascade was evaluated
because complementary evidence was not established.

## Decomposition assessment

Yes: the staged design converts an opaque “final contract wrong” outcome into
observable span, role, mapping, normalization, and validation evidence. The
deterministic refinement materially improves CONTEXT_ONLY and PREFERRED
handling while preserving zero False REQUIRED/EXCLUDED. The model arm remains
incomplete and blocks a clean deterministic-vs-model conclusion.

## Next decision

**E — Evidence invalid/incomplete.** The deterministic arm meets the frozen
development targets, but the model-assisted arm did not produce valid
phrase-level role evidence. One further bounded refinement of the model output
contract may be proposed only after Founder review; Gate 4 is not authorized.
