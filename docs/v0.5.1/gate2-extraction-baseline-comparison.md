# v0.5.1 Gate 2 — Extraction Baseline Comparison

**Work Object:** `armie-retrieval-v051-gate2-extraction-baseline`

**Status:** Candidate-complete; `READY_FOR_FOUNDER_ACCEPTANCE`.

This is an interpretation-layer development comparison. It does not establish
production readiness, remove confirmation, improve retrieval quality, or
execute C1.

## Company OS preflight

P0, Gate 0, and Gate 1 were founder-accepted; Gate 2 was explicitly
authorized. Gate 3 remains inactive. The active Work Object and scope are
recorded in `company-os/CURRENT_WORK.md`.

## Experimental question and common contract

The question is which bounded strategy converts the same natural-language
requests into CandidateInterpretation v1 while minimizing false HARD behavior.
Every arm receives the same request and authoritative registry identity
`v0.5-c1-capability-registry-1`, and emits
`nl-constraint-interpretation-v1` or an explicit not-run/invalid result. No arm
creates a `RetrievalContract`, Elasticsearch DSL, or C1 execution.

## Development benchmark identity

- Benchmark: `v0.5.1-nl-contract-extraction-v1`
- Items: **20**
- Fixture: `tests/fixtures/v051_gate1_gold.jsonl`
- Fingerprint: `924fe087dfe5716e07e874738ea132fa87df3a68a467f4eb6fce1bf65dedb605`
- Schema: `nl-constraint-interpretation-v1`
- Registry: `v0.5-c1-capability-registry-1`
- Serialization: canonical UTF-8 JSONL, SHA-256

The fixture is a bounded development set, not the final promotion or held-out
benchmark. It covers semantic-only, numeric, categorical, role, seniority,
location, exclusions, conjunction, SOFT preference, ambiguity, contradiction,
unknown category, unsupported temporal/relationship meaning, paraphrase, and
hard-negative over-extraction.

Gold was audited for schema validity, registry fields/operators, state labels,
HARD/SOFT polarity, exclusions, unsupported items, contradictions, and
duplicates before comparison. Gold was then frozen under the fingerprint above.

## Extractor arms

### Arm A — `rule-baseline-v1`

Conservative regular-expression/rule baseline. It handles only explicit
numeric operators, exact registry categories, clear exclusions, obvious
seniority/role/location requirements, and clear mandatory phrases. It abstains
on vague or unsupported meaning and preserves source phrases.

### Arm B — `ollama-structured-qwen3-4b-v1`

Structured-output Ollama arm using local `qwen3:4b`, temperature `0`, explicit
registry input, JSON output, and deterministic post-validation. It was run on a
bounded first-eight-item sample because model latency is material; this is not
a full benchmark comparison.

### Arm C — `hybrid-rule-plus-structured-qwen3-4b-v1`

Gate 0’s conservative hybrid hypothesis. Rules own explicit evidence; the
model may propose broader interpretations, but the current reconciliation keeps
rule evidence authoritative and exposes the arm identities. It was run on the
same first-eight-item sample as Arm B. It never executes retrieval.

Arm D was omitted because it would duplicate Arm B’s fully structured-output
mode.

## Results

Full run artifact:
[gate2-comparison-results.json](gate2-comparison-results.json)

| Arm | Scope | Exact match | False HARD query rate | Missed HARD query rate | Constraint precision | Constraint recall | Unsupported accuracy | Mean ms | p50 ms | p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Rule baseline | 20/20 | 75.0% | 0.0% | 10.0% | 100.0% | 95.0% | 90.0% | 0.13 | 0.04 | 0.22 |
| Ollama structured | 8/20 sample | 0.0% | 0.0% | 50.0% | 50.0% | 50.0% | 87.5% | 2687 | 2709 | 3533 |
| Conservative hybrid | 8/20 sample | 75.0% | 0.0% | 12.5% | 100.0% | 93.75% | 87.5% | 3090 | 2899 | 3375 |

Boolean metrics are reported separately from slot counts. No aggregate score
hides safety failures. False-exclusion count is included in each per-item
evaluation record.

### Per-stratum observations

The rule arm completed all 20 strata items. It was exact on numeric, category,
role, seniority, location, exclusion, conjunction, SOFT, semantic-only, range,
maximum, temporal, and relationship examples. Misses occurred on contradiction,
mixed supported/unsupported, paraphrase, and unknown-category handling. Its
false-HARD rate remained zero.

The model and hybrid arms were evaluated on the same first eight items only,
covering semantic-only, numeric, exclusion, SOFT, unsupported, ambiguity,
contradiction, and hard-negative cases. Hybrid matched the rule baseline on
these sampled strata; the model-only arm missed numeric, exclusion, unsupported,
and contradiction details.

## False-HARD analysis

No arm produced a false HARD event in the recorded runs. The development set
contains explicit preference, vague-number, contextual, unsupported, and
semantic-only traps. This is encouraging safety evidence, not a promotion
threshold or production claim.

## Missed-HARD and failure analysis

Rule misses are concentrated in:

- contradiction state completion;
- mixed supported plus unsupported requests;
- paraphrase/ambiguity boundaries;
- unknown-category handling.

The model-only sample additionally missed explicit numeric and exclusion
details and dropped unsupported meaning. Hybrid preserved rule-level recall on
the sample but adds model latency and has not been evaluated over all 20 items.

The taxonomy used for later error analysis is: preference hardened, vague
numeric hardened, contextual category/location, unsupported relationship,
negation misread, alias overreach, hallucinated field/value, conjunction scope,
numeric miss, exclusion miss, normalization failure, and over-abstention.

## Unsupported, ambiguity, contradiction, and semantic-only behavior

Semantic-only over-extraction was zero for all recorded runs. Unsupported
meaning remains visible in the rule and hybrid outputs; model-only output was
less reliable on the sampled unsupported item. Contradiction handling is a
known weakness: the rule and hybrid sample report a missed contradiction-state
match, while model output did not reliably preserve it.

## Repeatability and latency/cost

The rule arm is deterministic and sub-millisecond on this fixture. The Ollama
and hybrid samples used temperature zero and the same local model configuration;
their recorded outputs are repeatable for the bounded run, but no repeated
stability study was promoted from this small sample. Model call latency is
approximately 2.7–3.5 seconds per request on this environment. Token cost was
not exposed by the local API and is therefore reported as unavailable.

## Manual spot audit

The 20-item fixture is reviewable line-by-line. Representative cases include:

- clear `at least 20` HARD extraction;
- SOFT `prefer senior` language;
- semantic-only Azure request;
- Healthcare plus Financial Services exclusion;
- unsupported delivery and temporal meaning;
- contradictory numeric bounds;
- preference-hardening hard-negative;
- rule and model misses recorded in the JSON artifact.

## Candidate architecture outcome

**Outcome: E — Insufficient evidence for architecture promotion.**

The deterministic rule baseline is the safest current candidate: zero false
HARD events, 100% constraint precision, and 95% constraint recall on all 20
development items. The conservative hybrid is promising on the eight-item
sample, but model-arm coverage is incomplete and adds substantial latency. No
arm is production-ready or accepted as the v0.5.1 production architecture.

## Gate 3 recommendation

If authorized later, Gate 3 should use a larger frozen benchmark, explicit
false-HARD promotion thresholds, paraphrase robustness, repeated-run
stability, contradiction/unsupported failure decomposition, and a complete
model/hybrid comparison. It must retain mandatory confirmation and must not
execute NL-derived contracts without a separate authorization.

## Validation status

The focused Gate 1/Gate 2 interpretation suite passes (**14 tests**), Python
compilation passes with an isolated cache, Markdown links resolve, and
`git diff --check` passes. The repository-wide Python suite was also run
(**149 tests, 3 skipped**); the 3 Workbench failures are pre-existing
environment/artifact availability failures because the external v0.5.0
Workbench benchmark payload under `/tmp/armie-v040-dataset-v2-full` is absent
(`manifest.json`, v2 queries/judgements, and experts). No Gate 2 test failed.
The missing payload was not regenerated here because that would leave the
bounded interpretation comparison and begin unrelated Workbench/data work.

## P0 debt and stop condition

Healthcare-positive retrieval coverage, raw corpus prevalence, and historical
mapping fingerprint metadata remain visible P0 carry-forward items. They do not
block this interpretation-only Gate 2, but Healthcare coverage blocks future
end-to-end extraction→C1 evaluation.

Gate 2 stops here. No Workbench integration, C1 execution, Gate 3, commit, tag,
or push was started.
