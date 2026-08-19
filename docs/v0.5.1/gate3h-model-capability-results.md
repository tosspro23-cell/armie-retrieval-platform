# Gate 3H — Stage 1/2 Semantic Model Capability Study

**Status:** Candidate-complete / READY_FOR_FOUNDER_ACCEPTANCE
**Decision:** C — no tested model provides sufficient value over deterministic staging
**Gate 4:** Inactive

Gate 3G-R was accepted by the Founder with Decision B (no promotion), and this
bounded capability study was authorized. It did not modify the valid held-out
benchmark, deterministic extractor, Stage 3–6 semantics, C1, or Workbench.

## Frozen model contract

The model performs one joint Stage 1/2 operation: phrase-level span detection
and one of the frozen roles REQUIRED, EXCLUDED, PREFERRED, CONTEXT_ONLY,
UNSUPPORTED, or AMBIGUOUS. It must return contiguous request text where
possible, preserve role-bearing context, and never emit prompt text, isolated
registry tokens, runtime predicates, or RetrievalContract objects. Deterministic
Stages 3–6 remain downstream and unchanged.

## Development evidence

| Field | Value |
|---|---|
| Fixture | `v0.5.1-gate3fr-staged-dev-validation-v1` |
| Scope | 36 prospective development requests; not Gate 3G-R held-out data |
| Candidate reference | `deterministic-staged-v2-gate3fr` |
| qwen reference | `qwen3:4b`, prior checkpointed run, 36/36 terminal but phrase output invalid/incomplete |
| stronger model | `qwen3:8b`, 36/36 model calls, no fallback |
| prompt/task | `staged-qwen3-4b-span-role-v1` contract, model identity varied only |
| runtime | local Ollama; CPU/local runtime; no production integration |

## Results

| Metric | Deterministic | qwen3:4b reference | qwen3:8b |
|---|---:|---:|---:|
| Phrase-level validity | valid deterministic spans | invalid/incomplete | 0.99% precision / 2.70% recall against exact gold phrases |
| Role accuracy | 86.11% | invalid comparison | 0% |
| False REQUIRED | 0% | not reliable | 13.89% |
| False EXCLUDED | 0% | not reliable | 25.00% |
| REQUIRED accuracy | 100% | invalid | 0% |
| EXCLUDED accuracy | 100% | invalid | 0% |
| PREFERRED accuracy | 85.71% | invalid | 0% |
| CONTEXT_ONLY accuracy | 100% | invalid | 0% |
| UNSUPPORTED accuracy | 66.67% | invalid | 0% |
| AMBIGUOUS accuracy | 66.67% | invalid | 0% |
| mean / p50 / p95 latency | 0.17 / 0.08 / 0.24 ms | prior run not comparable | 5,508 / 4,007 / 14,560 ms |

The qwen3:8b model produced role-labelled token fragments (for example,
`must`, `have`, `at`, `least`, `15`, `years`) rather than phrase-level spans.
This violates the interface contract and also caused unsafe hardening. No
supported precision/recall or final False-HARD claim is made for the model arm;
the output is rejected before downstream interpretation. The deterministic
reference remains the only valid downstream diagnostic on this fixture.

## Repeatability and operational observations

The qwen3:8b arm completed one bounded pass with 36 model calls and durable
checkpoints. Representative-category repeatability was not promoted to a
separate tuning loop because the first-pass phrase contract already failed;
additional retries would constitute prohibited iterative tuning. Latency was
model-dominated and materially higher than deterministic staging.

## Decision and boundary

**Decision C:** neither the prior qwen3:4b arm nor qwen3:8b provides a valid,
safe Stage 1/2 capability lift over deterministic staging. Do not create a
model-assisted candidate, cascade, Gate 4 integration, C1 path, or Workbench
change. A future gate would need a new structured-output method or model
interface study with an independently frozen development contract.

Machine evidence is retained in ignored local checkpoints:

- `.artifacts/gate3fr-model-checkpoint.json`
- `.artifacts/gate3h-qwen8b-checkpoint.json`

This is controlled synthetic development evidence and must not be generalized
to production expert-search quality.
