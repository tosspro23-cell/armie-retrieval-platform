# Gate 3C — Resumable model-evaluation harness

**Status:** candidate-complete; Gate 3 remains pending founder acceptance. Gate 4 remains inactive.

Gate 3C repaired only evaluation execution. The 120-item benchmark, gold labels,
prompt, schema, registry, decoding, timeout/retry policy, and promotion thresholds
remain those frozen by Gate 3.

## Failure diagnosed before the repair

The Gate 3B runner held results in process memory and wrote one report only after the
arm returned. A bounded Codex/shell execution window terminated the long-running
model process before the report write, so the report recorded `attempted=120,
completed=0` even though requests had already been issued. This was distinct from
the per-request Ollama timeout: Gate 3C retains a 15-second request timeout and at
most one retry. The process/window limit and per-request timeout are reported
separately.

## Harness contract

`run_v051_gate3c_resumable.py` writes one JSON object to a durable JSONL checkpoint
immediately after each item reaches a terminal status. It records `SUCCESS`,
`MODEL_CALL_FAILURE`, `STRUCTURED_OUTPUT_FAILURE`, `SCHEMA_VALIDATION_FAILURE`,
`ABSTENTION`, and `TIMEOUT`. A sidecar identity manifest refuses resume/merge when
any of the following differs: benchmark fingerprint, arm/model identity, prompt,
schema, registry, timeout, retry policy, or decoding settings.

The logical run ID is independent of operational shards. Resume skips terminal IDs,
rejects duplicate IDs, and final aggregation requires exactly the expected IDs with
no missing or duplicate records. The harness performs no concurrency and does not
change extractor semantics. The local Ollama client used its default keep-alive
behaviour; no model reload was forced between items or shards. Cold model-load timing
was measured separately during Gate 3B (approximately 4,756.5 ms); the Gate 3C
per-item timings below are warm/request-plus-orchestration timings.

## Development validation

A real three-item qwen3:4b run completed 3/3 in 10.48 seconds. A forced process
interruption after item 1 left one durable checkpoint row; resume completed the
remaining two items with no duplicate execution. Harness tests also verify identity
mismatch refusal. This was infrastructure validation, not semantic tuning.

## Frozen 120-item execution

| Arm | Attempted | Terminal | Structured success | Infrastructure failures | Structured failures | Wall clock | Model-time sum |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen3:4b model | 120 | 120 | 120 | 0 | 0 | 306.40 s | 306.22 s |
| qwen3:4b hybrid | 120 | 120 | 120 | 0 | 0 | 348.25 s | 348.06 s |

Both runs passed checkpoint integrity: 120 represented, zero duplicates, zero missing,
and all rows terminal. The model run used identity
`ollama-structured-qwen3-4b-v1-gate3b-warm-persistent-v1`; the hybrid run used
`hybrid-rule-plus-structured-qwen3-4b-v1-gate3b-warm-persistent-v1`. Full checkpoints were retained
outside the repository under `/tmp/armie-gate3c-model.jsonl` and
`/tmp/armie-gate3c-hybrid.jsonl`; the tracked summary is
`gate3c-evaluation-results.json`.

### Model frozen semantic metrics

| Metric | Model | Frozen threshold | Result |
|---|---:|---:|---|
| Coverage | 100% | 100% | PASS |
| Exact candidate contract | 0.00% | >=80% | FAIL |
| False HARD query | 0.00% | 0% | PASS |
| False HARD constraint rate | 0.00% | 0% | PASS |
| False exclusion | 0.00% | 0% | PASS |
| Semantic-only over-extraction | 0.00% | 0% | PASS |
| Unsupported preservation | 80.00% | >=90% | FAIL |
| Contradiction detection | 95.00% | >=90% | PASS |
| Constraint precision | 30.00% | >=95% | FAIL |
| Constraint recall | 30.00% | >=85% | FAIL |

Model latency: mean 2,551.8 ms, p50 2,489.7 ms, p95 3,257.6 ms; total model
request time 306.22 s versus 306.40 s wall clock. No retries or timeouts occurred.
The model arm is therefore operationally complete but does not satisfy the frozen
semantic promotion criteria.

### Hybrid comparison

Hybrid completed the same 120 items with the same checkpoint contract. It reproduced
the frozen rule-authoritative semantic profile: exact 28.33%, false HARD query 9.17%,
false HARD constraint rate 9.17%, false exclusion 0%, unsupported preservation
82.50%, contradiction 95.83%, precision 66.25%, and recall 62.78%. It fails the
frozen promotion thresholds and is not promoted.

Hybrid latency: mean 2,900.5 ms, p50 2,883.1 ms, p95 3,614.4 ms; total model/request
time 348.06 s versus 348.25 s wall clock. No retries or timeouts occurred.

## Repeatability

The first six frozen records were run three times with the same model identity,
prompt, schema, registry, timeout, and decoding. Exact `CandidateInterpretation`
stability was 100% for both comparisons against the first run; HARD-contract
stability was 100%. This is a small representative repeatability check, not a
statistical guarantee for all future runs.

## Gate decision

The harness repair resolves the execution-coverage blocker: qwen3:4b is now
reliably auditable over all 120 items. The model and hybrid arms nevertheless fail
frozen semantic thresholds. Gate 3 is **ACTIVE / BLOCKED on semantic promotion**;
no extractor architecture is promoted and Gate 4 remains inactive. Any future
model/prompt change requires a separately authorized decision; this task did not
tune or switch models.
