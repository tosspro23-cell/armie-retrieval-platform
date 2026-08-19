# v0.5.1 Gate 3 — Frozen Extraction Evaluation

**Work Object:** `armie-retrieval-v051-gate3-frozen-extraction-evaluation`
**Status:** Candidate-complete for review; **READY_FOR_FOUNDER_ACCEPTANCE** is
not yet asserted because model-arm coverage is incomplete.

## Scope and safety boundary

Gate 3 evaluates Natural Language → `CandidateInterpretation` only. It does
not compile or execute a `RetrievalContract`, call C1, integrate Workbench, or
remove mandatory confirmation. Gate 2's 20-item development fixture and
results remain immutable historical evidence.

## Frozen benchmark

- Benchmark: `v0.5.1-nl-constraint-extraction-eval-v1`
- Fixture: `tests/fixtures/v051_gate3_eval.jsonl`
- Items: **120** (20 strata × 6 controlled variants)
- Fingerprint: `74f19a21dffe975c97673736fe33292ee7d5a286b3d612e007dfe4b1008df800`
- Schema: `nl-constraint-interpretation-v1`
- Registry: `v0.5-c1-capability-registry-1`
- Manifest: [gate3-evaluation-manifest.json](gate3-evaluation-manifest.json)

The fixture was fingerprinted before arm execution. It includes semantic-only,
numeric, paraphrase, vague numeric, industry, role, seniority, location,
exclusion, conjunction, SOFT preference, ambiguity, contradiction, unknown,
unsupported temporal/relationship, mixed, and hard-negative challenge strata.

## Frozen promotion criteria

Criteria were recorded in the manifest before the run:

- full-set coverage: 100%;
- False HARD query and constraint rates: 0%;
- false exclusion: 0%;
- semantic-only over-extraction: 0%;
- unsupported preservation ≥90%; contradiction detection ≥90%;
- exact match ≥80%; precision ≥95%; recall ≥85%;
- repeatability stability ≥95%.

Safety failures take precedence over recall gains. These are candidate-only
promotion thresholds and do not authorize autonomous execution.

## Frozen arm identities

| Arm | Identity | Coverage attempted | Completed |
|---|---|---:|---:|
| Rules | `rule-baseline-v2-gate3` | 120/120 | 120 |
| Structured model | `ollama-structured-qwen3-4b-v1-gate3` | 20/120 bounded diagnostic | 0 |
| Hybrid | `hybrid-rule-plus-structured-qwen3-4b-v1-gate3` | 20/120 bounded diagnostic | 0 |

The model and hybrid attempts were bounded after the full-set local Ollama run
exceeded the available execution window. Every attempted call was classified
as an infrastructure/model-call failure; no conditional semantic metric is
reported for those arms.

## Results using full frozen denominators

| Arm | Exact match | False HARD query | False HARD constraint | Precision | Recall | Unsupported preserved | Mean / p50 / p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Rules (n=120) | 28.33% | **9.17%** | 16.67% | 66.25% | 62.78% | 82.50% | 0.046 / 0.031 / 0.071 |
| Model (n=120 denominator; 20 attempted) | not estimable | not estimable | not estimable | not estimable | not estimable | not estimable | not estimable |
| Hybrid (n=120 denominator; 20 attempted) | not estimable | not estimable | not estimable | not estimable | not estimable | not estimable | not estimable |

The rule arm has complete coverage but fails the frozen safety thresholds. The
largest False HARD strata were seniority (100% of six), ambiguous (50%),
industry (33%), contradiction (17%), exclusion (17%), and range (17%).
False HARD cases are retained in the machine-readable artifact rather than
repaired after seeing results.

## Unsupported, contradiction, and semantic-only findings

- Semantic-only over-extraction: 0% for the completed rule arm.
- Unsupported preservation: 82.5%, below the 90% threshold.
- Contradiction state detection: 95.83%; this passes the provisional threshold,
  but does not offset the safety failures.
- Unsupported, schema, and infrastructure failures are separate fields in the
  result artifact; a model timeout is not counted as a semantic error.

## Repeatability and robustness

The deterministic rule arm was run twice over all 120 items: interpretation and
HARD-contract stability were both 100%. Model/hybrid repeatability and
paraphrase stability are **not characterized** because no model outputs
completed in the bounded diagnostic run. Gate 3 therefore cannot claim full
cross-arm robustness.

## Pairwise analysis

No pairwise wins/ties/losses are reported for model or hybrid because there are
zero common completed items. This is an explicit coverage result, not a hidden
conditional comparison. Safety precedence remains the frozen win rule.

## Architecture decision

**Decision: E — INCONCLUSIVE — infrastructure/evaluation evidence
insufficient.**

No extractor is promoted. Rules fail the frozen False HARD and correctness
thresholds; model and hybrid require a reproducible full-set execution path
before comparison. Gate 4 remains inactive.

## Gate 4 recommendation

Do not begin Gate 4. First resolve local Ollama throughput/timeout behavior,
run all three arms over the full 120-item frozen set, characterize model and
hybrid repeatability/paraphrases, and then re-evaluate the pre-registered
criteria without changing the benchmark after observing results.

## Validation and artifact dependency

- Focused Gate 1/Gate 2 tests: 14 passed.
- Full Python suite: **149 passed, 6 skipped**. The three optional Workbench
  tests now skip explicitly when the external v0.5.0 10K payload is absent;
  this dependency is no longer an unexplained red test.
- Python compilation with isolated cache: passed.
- Markdown link check: passed (0 missing local links).
- `git diff --check`: passed.

The external Workbench benchmark payload remains optional and was not
regenerated. No Elasticsearch, Workbench, C1, Gate 4, commit, tag, or push was
started.

Machine-readable results: [gate3-evaluation-results.json](gate3-evaluation-results.json).
