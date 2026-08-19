# Gate 3D — Interpretation semantics refinement

**Status:** candidate-complete; Gate 3 architecture decision: **D — NO PROMOTION**.
Gate 3C evidence was accepted by the founder; Gate 4 remains inactive.

Gate 3D changed only interpretation-layer development arms. The frozen benchmark,
gold labels, prompt identities used by historical arms, schema, registry, decoding,
thresholds, and mandatory confirmation boundary were preserved.

## Rule failure refinement

`RuleExtractorV3` (`rule-conservative-v3-gate3d`) makes the requirement boundary
explicit: a mention or descriptive context is not an eligibility predicate. A
categorical HARD constraint requires explicit requirement language (`must`,
`required`, `only`, or an equivalent approved construction). Preferences remain
SOFT, vague numeric language such as `around 20` remains unresolved, exclusions
require explicit exclusion language, and normalized positive/exclusion and numeric
bounds are checked for contradictions.

This is a conservative parser, not a larger keyword list. Development evidence
showed zero False-HARD query events on the 20-item Gate 2 fixture and 95% slot
precision, while preserving 90% slot recall. The frozen run reduced Rule v2's
False-HARD query rate from 9.17% to 6.67%, but did not reach the frozen 0% safety
threshold.

## Model and cascade refinement

`OllamaStructuredExtractorV2` (`ollama-structured-qwen3-4b-v2-gate3d`) adds explicit
instructions for HARD evidence, conjunction completeness, operator normalization,
unsupported preservation, registry authority, and conservative abstention. It
keeps the same CandidateInterpretation v1 output and deterministic validation.
Development model output remained conservative: zero False-HARD, but only 35%
precision and 35% recall on the 20-item fixture. This indicates under-extraction
and decomposition/schema difficulty, not an infrastructure failure.

`CascadeExtractorV2` (`cascade-conservative-v2-gate3d`) routes fully resolved,
non-ambiguous, non-unsupported requests through Rule v3. Uncertain requests invoke
Model v2; reconciliation never lets a model-only HARD proposal silently become an
executable requirement. This is a safety-first candidate interpretation, not C1.
On the development fixture it invoked the model for 20% of items, retained zero
False-HARD events, and had 95% precision / 90% recall. The cascade is materially
cheaper than calling the model for every item, but it does not eliminate Rule v3's
semantic failures.

## Frozen benchmark identity

- Benchmark: `v0.5.1-nl-constraint-extraction-eval-v1`
- Items: 120
- Fingerprint: `74f19a21dffe975c97673736fe33292ee7d5a286b3d612e007dfe4b1008df800`
- Harness: `gate3c-resumable-v1`
- Registry: `v0.5-c1-capability-registry-1`
- Schema: `nl-constraint-interpretation-v1`

All three refined arms completed 120/120 terminal items with zero infrastructure
or structured-output failures. Checkpoint integrity was 120 represented, zero
missing, and zero duplicates for every arm. Machine-readable details are in
[gate3d-evaluation-results.json](gate3d-evaluation-results.json).

## Frozen results

| Arm | False HARD query | Exact | Precision | Recall | Unsupported | Contradiction | Mean latency | p50 | p95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Rule v2 historical | 9.17% | 28.33% | 66.25% | 62.78% | 82.50% | 95.83% | sub-ms | sub-ms | sub-ms |
| Rule v3 | 6.67% | 24.17% | 59.58% | 55.00% | 82.50% | 96.67% | 0.050 ms | 0.033 ms | 0.047 ms |
| Model v1 historical | 0% | 0% | 30.00% | 30.00% | 80.00% | 95.00% | 2.55 s | 2.49 s | 3.26 s |
| Model v2 | 0% | 0% | 30.00% | 30.00% | 80.00% | 95.00% | 5.66 s | 5.71 s | 6.14 s |
| Hybrid v1 historical | 9.17% | 28.33% | 66.25% | 62.78% | 82.50% | 95.83% | 2.90 s | 2.88 s | 3.61 s |
| Cascade v2 | 6.67% | 23.33% | 59.58% | 55.00% | 80.83% | 96.67% | 1.35 s | 0.13 ms | 5.19 s |

The cascade used Rules-only for 87/120 items and invoked Model v2 for 33/120
(27.5%). Its p50 reflects the fast path; p95 reflects model-path latency.

## Per-stratum and repeatability

The complete machine summary retains per-item metrics and stratum labels. Rule v3
and Cascade v2 retain the semantic-only and SOFT safety boundary, but remain weak
on conjunction, contradiction, unsupported, temporal, and relationship strata.
Model v2 produced no exact contract matches and did not improve the v1 semantic
profile.

Cascade repeatability used six representative frozen items, three runs, and the
same resumable harness: exact interpretation stability 100%; HARD-contract
stability 100%. No candidate passed the frozen thresholds, so this is evidence of
repeatable behavior, not promotion evidence.

## Frozen threshold decision

The thresholds were not changed. Every refined arm fails at least one mandatory
criterion, and Rule v3/Cascade v2 still violate the 0% False-HARD requirement.
Therefore the final architecture decision is:

**D — NO PROMOTION — semantics remain below thresholds.**

The bounded next step is another authorized semantic improvement or reconsideration
of v0.5.1 scope. Gate 4 must not begin from this result.
