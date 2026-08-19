# v0.5.1 Gate 1 — Interpretation Schema & Benchmark Foundation

**Work Object:** `armie-retrieval-v051-gate1-interpretation-benchmark-foundation`

**Status:** Candidate-complete; `READY_FOR_FOUNDER_ACCEPTANCE`.

**Scope:** Deterministic schema, annotation contract, benchmark design, and
evaluator foundation. Gate 1 does not select or implement a production
extractor.

## 1. Company OS and carry-forward state

P0 is accepted with carry-forward conditions. Gate 0 is founder-accepted and
Gate 1 is authorized. Gate 2 remains inactive. The raw coverage, historical
mapping-fingerprint, and Healthcare-positive corpus conditions from P0 remain
later-stage evidence requirements. Released v0.5.0 Dataset v2 is immutable.

## 2. Frozen evaluation purpose

The benchmark evaluates:

```text
Natural-language request → candidate interpretation
```

It does not primarily evaluate retrieval ranking. Interpretation evaluation,
known-contract C1 retrieval evaluation, and end-to-end evaluation remain three
separate layers.

## 3. CandidateInterpretation schema

Schema identity: **`nl-constraint-interpretation-v1`**.

The deterministic schema is implemented in
`src/armie_retrieval/interpretation/models.py`. It contains:

- request identity and original request;
- semantic query;
- candidate constraints and exclusions;
- SOFT preferences;
- unsupported, unresolved, and contradiction items;
- deterministic interpretation state;
- registry identity;
- normalization and optional evidence/source-span metadata;
- schema version.

`CandidateInterpretation` is deliberately distinct from
`RetrievalContract`. It has no compile or execution method and cannot directly
reach C1.

Each candidate constraint records field, operator, raw value, normalized value,
polarity, HARD/SOFT strength, support and ambiguity state, source span, and
optional rationale.

## 4. Interpretation states and precedence

The frozen state vocabulary is:

`INTERPRETED`, `NEEDS_CONFIRMATION`, `AMBIGUOUS`, `PARTIALLY_SUPPORTED`,
`UNSUPPORTED`, `CONTRADICTORY`, and `NO_HARD_CONSTRAINTS`.

Precedence is deterministic: `CONTRADICTORY` first; then `AMBIGUOUS` when
uncertainty prevents a stable supported candidate; then `PARTIALLY_SUPPORTED`
when supported constraints coexist with unsupported meaning; then
`UNSUPPORTED` when no executable supported meaning exists; then
`NEEDS_CONFIRMATION` for supported HARD/exclusion candidates; and
`NO_HARD_CONSTRAINTS` for semantic-only or SOFT-only requests. `INTERPRETED`
is reserved for a complete candidate that requires no unresolved confirmation
under the selected policy.

## 5. Gold annotation policy

Gold HARD requires semantic support from the request, not keywords alone.
Mandatory language (`must`, `required`, `only`, `at least`, `no less than`,
`exclude`, `cannot`, `must not`), supported numeric operators, exact
categorical requirements, conjunctions, and explicit exclusions are annotated
as HARD when coherent and registry-supported.

Preference language (`prefer`, `ideally`, `nice to have`, `bonus`, `around`,
`approximately`) is never silently HARD. Gate 1 stores it as a SOFT item or
semantic preference; no soft-ranking runtime is introduced.

Positive requirements and exclusions are separate slots. `Healthcare` is
`industry = healthcare`; `excluding Financial Services` is
`industry != financial services` with exclusion polarity.

Numeric rules preserve operator semantics: `at least`/`20+` → `gte`, `more
than` → `gt`, `exactly` → `eq`, `under` → `lt`, and explicit ranges → `between`.
Vague expressions such as `around 20` remain ambiguous unless a later policy
explicitly defines them. Unsupported operators remain unsupported.

Categorical values normalize only through the authoritative registry and its
approved aliases/display labels. Unknown or ambiguous categories are not
invented.

## 6. Safety events and matching

A **False HARD** event occurs when a prediction introduces a hard eligibility
predicate or exclusion unsupported by the gold meaning. It is reported at both
constraint and query level. A **Missed HARD** event occurs when a gold HARD
constraint or exclusion is absent from the prediction. The two events remain
separate because false HARD is the primary safety risk.

Constraint equivalence requires matching field, operator, normalized value,
polarity, and HARD/SOFT state. `gte 20` and `gt 20` are not equivalent; a
display label that normalizes to the same canonical value is equivalent.

Exact Candidate Contract Match requires exact supported HARD constraints,
exclusions, canonical normalization, unsupported items, contradiction state,
and critical state fields. Semantic-query quality is evaluated separately and
does not contaminate exact contract scoring.

## 7. Metric hierarchy

Safety priority:

1. False HARD query rate
2. False HARD constraint rate
3. False exclusion rate

Correctness and coverage:

4. Exact candidate-contract match
5. Constraint precision/recall
6. Field/operator/value/polarity accuracy
7. Missed HARD rate
8. Supported extraction recall

Governance:

9. Unsupported detection precision/recall
10. Ambiguity and contradiction accuracy

No promotion thresholds are frozen in Gate 1.

## 8. Benchmark identity, strata, and size policy

Benchmark family identity:
**`v0.5.1-nl-contract-extraction-v1`**.

Manifest: [`gate1-benchmark-manifest.json`](gate1-benchmark-manifest.json).
It binds schema identity, registry identity, annotation policy, serialization,
strata, split policy, and SHA-256 canonical JSONL fingerprinting.

Strata cover semantic-only, numeric minimum/maximum/range/vague numeric,
industry, role, seniority, location, exclusions, conjunctions, preference vs
requirement, ambiguity, contradiction, unknown category, mixed
supported/unsupported, temporal and relationship unsupported meaning,
paraphrase, and hard-negative over-extraction cases.

The staged size policy is intentionally evidence-led: a small manually
inspectable development fixture first, followed by balanced frozen validation
and held-out test sets sized for per-stratum error analysis. Gate 1 does not
choose an arbitrary large corpus or generate the frozen benchmark.

Development data may tune prompts later; validation and test data remain frozen
and must not be repeatedly used for tuning or promotion.

## 9. Hard-negative interpretation subset

The benchmark must challenge over-extraction with strong preferences, vague
numbers, contextual industries or employers, non-exclusion negative language,
and semantic words that resemble registry categories without expressing
eligibility. The included eight-item fixture contains a preference-hardening
case and semantic-only cases.

## 10. Annotation and artifact governance

Future gold workflow:

```text
draft request → semantic annotation → HARD/SOFT/exclusion annotation
→ registry normalization → unsupported/ambiguity/contradiction labels
→ independent review → adjudication → freeze
```

Deterministic checks must reject invalid schema, unknown registry values,
unsupported operators, impossible states, contradictions, duplicates, and
inconsistent labels. JSONL is UTF-8, canonically ordered, reviewable, and
fingerprinted with SHA-256.

Extraction benchmark, retrieval corpus, and end-to-end fixture each receive a
separate identity, checksum, and lineage. Future Healthcare-positive fixtures
must be newly versioned; they must not mutate v0.5.0 Dataset v2.

## 11. Gate 2 contract and strategy boundary

Every Gate 2 extractor arm must emit `CandidateInterpretation` schema v1 using
the same input, registry identity, benchmark, and evaluator. Candidate arms may
later include deterministic rules, LLM structured extraction, constrained
structured output, and hybrid approaches. Gate 1 does not implement or compare
these arms and does not bias language toward a model.

The selected hypothesis for later evaluation is conservative hybrid extraction
plus deterministic schema validation plus mandatory user confirmation. Model
output remains untrusted; it cannot issue DSL, execute C1, mutate validated
semantics, or discard unsupported meaning.

Synthetic/non-sensitive requests are required for future benchmark material.
External model calls require separate privacy and logging review.

## 12. Implementation and verification

Allowed Gate 1 implementation is limited to:

- schema models;
- deterministic structural validation;
- candidate matching and metric calculation;
- manifest/fingerprint helpers;
- a small hand-reviewable fixture;
- unit tests.

Implemented files:

- `src/armie_retrieval/interpretation/models.py`
- `src/armie_retrieval/interpretation/evaluator.py`
- `src/armie_retrieval/interpretation/serialization.py`
- `tests/test_v051_gate1_interpretation.py`
- `tests/fixtures/v051_gate1_gold.jsonl`

The fixture has eight manually inspectable cases spanning semantic-only,
numeric HARD, exclusion, SOFT preference, mixed unsupported meaning,
ambiguity, contradiction, and hard-negative over-extraction. Tests use
hand-calculated slot outcomes and deliberately wrong predictions for false
HARD, missed HARD, operator/value, exclusion, preference hardening,
unsupported omission, contradiction, and exact-match behavior.

No extractor, model, endpoint, Workbench integration, benchmark generation,
released-data modification, C1 change, Gate 2, commit, tag, or push was
started.

## Candidate disposition

Gate 1 is candidate-complete if the deterministic test and static validation
matrix passes. The Result Package is then `READY_FOR_FOUNDER_ACCEPTANCE`.
Gate 2 remains inactive and requires a new founder decision.
