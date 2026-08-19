# Gate 3F — Staged Interpretation Development Validation

**Status:** Candidate-complete; READY_FOR_FOUNDER_ACCEPTANCE
**Scope:** Development-only architecture validation. Gate 3F did not modify the
historical frozen 120-item benchmark, C1/Workbench, RetrievalContract,
thresholds, datasets, or Gate 4.

## Company OS and boundaries

Gate 3E was accepted and the active Work Object is
`armie-retrieval-v051-gate3f-staged-interpretation`. The staged architecture is
candidate-only. The interim safety boundary is explicit-requirement-only:
only REQUIRED and EXCLUDED roles can enter supported mapping; PREFERRED,
CONTEXT_ONLY, UNSUPPORTED, and AMBIGUOUS never become hard predicates.

## Staged contract

```text
constraint-bearing spans
  -> semantic role
  -> registry mapping
  -> operator/value normalization
  -> deterministic validation
  -> CandidateInterpretation assembly
```

The six versioned stage identities are `constraint-span-v1`,
`interpretation-role-v1`, `registry-mapping-v1`,
`constraint-normalization-v1`, `staged-interpretation-v1`, and the existing
`nl-constraint-interpretation-v1` candidate contract. Each stage has typed
dataclasses and can be tested independently.

### Role ontology

- `REQUIRED`: explicit eligibility requirement.
- `EXCLUDED`: explicit disqualifying condition.
- `PREFERRED`: preference, not eligibility necessity.
- `CONTEXT_ONLY`: meaningful context that must not become eligibility.
- `UNSUPPORTED`: meaning outside the current registry/contract.
- `AMBIGUOUS`: insufficient evidence to harden safely.

Examples: “Healthcare experts only” is REQUIRED; “worked on Healthcare
products” is CONTEXT_ONLY; “preferably based in London” is PREFERRED; “around
20 years” is AMBIGUOUS. CandidateInterpretation remains non-executable.

## Development fixture

`tests/fixtures/v051_gate3f_development.json` is independently authored,
manually reviewable development evidence with artifact identity
`v0.5.1-gate3f-staged-dev-v1` and 24 varied cases. It covers requirements,
exclusions, preferences, context, unsupported temporal/relationship language,
ambiguity, numeric operators, negation, and semantic-only requests. It is not
a promotion benchmark and does not reuse frozen Gate 3 labels.

## Deterministic staged baseline

The baseline is implemented in `interpretation/staged.py`. It performs one
deterministic span/role pass followed by deterministic mapping, normalization,
validation, and assembly. On the 24-case development fixture:

| Metric | Result |
|---|---:|
| role accuracy | 70.83% |
| False REQUIRED rate | 0.00% |
| False EXCLUDED rate | 0.00% |
| CONTEXT_ONLY accuracy | 66.67% |
| PREFERRED accuracy | 33.33% |
| cases | 24 |
| deterministic latency mean / p50 / p95 | 0.117 / 0.038 / 0.055 ms |

The result demonstrates safety and attribution value, not production coverage.
The remaining role misses are visible at Stage 2 rather than being hidden in a
single final contract score.

## Model-assisted staged baseline

`ModelAssistedStagedExtractor` asks qwen3:4b only for spans and semantic roles;
all mapping, normalization, validation, and assembly remain deterministic.
The implementation records model-call count and falls back explicitly to the
deterministic baseline when Ollama is unavailable. A bounded fixture run was
attempted, but the local qwen3:4b request did not return within the bounded
window and was stopped; no model quality claim is made. This is an operational
blocker for a complete model-vs-deterministic comparison, not a silent result.

## Stage metrics and error propagation

The stage evaluator reports role accuracy, False REQUIRED, False EXCLUDED,
CONTEXT_ONLY accuracy, and PREFERRED accuracy. Mapping and normalization are
validated against the authoritative registry and operator capabilities.
Every assembled candidate carries span ID, source text, role, and stage
provenance. The first failing stage is therefore observable: a wrong hard
industry caused by context hardening is a Stage 2 error; a correct role with a
wrong field/operator is a Stage 3/4 error; rejected duplicates or unsupported
operators are Stage 5 errors.

## Historical one-shot comparison

Gate 3D frozen Rule v3 had 6.67% False HARD and 24.17% exact; qwen3:4b Model
v2 had 0% False HARD but 0% exact and 30% precision/recall. The staged baseline
has not been evaluated on that frozen set. Its demonstrated improvement is
architectural: explicit context/preference safety and stage attribution on
independent development evidence, not a promotion-metric claim.

## Model-call architecture and latency

The preferred model design is one bounded call for spans and roles per request,
followed by deterministic stages. It does not require one call per stage or
per span. Deterministic execution is sub-millisecond on the fixture. The
model-assisted latency distribution is not reported because the bounded local
run did not complete; no extrapolation is justified.

## Future held-out promotion requirements

A future promotion set must be prospectively authored after the staged schema
freezes, remain held out from tuning, and include span/role annotations,
CONTEXT_ONLY hard negatives, explicit requirements, exclusions, unsupported and
ambiguous language, registry/operator gold, and error-propagation labels. The
historical 120-item Gate 3 set remains diagnostic/regression evidence.

## Viability verdict and next gate

**B — Staged architecture promising but needs one bounded development
refinement.** The safety boundary and observability are materially improved,
but Stage 2 role coverage and the model-assisted comparison need one focused
development refinement before a held-out promotion gate is proposed.

The next recommendation is a bounded Gate 3F refinement (improve role-span
coverage and complete a time-boxed qwen3:4b comparison), not Gate 4. No next
gate is started by this Result Package.
