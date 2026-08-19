# v0.5.1 Gate 0 — Governed Natural Language Constraint Interpretation Charter

**Work Object:** `armie-retrieval-v051-gate0-governed-nl-contract`

**Status:** Candidate-complete; `READY_FOR_FOUNDER_ACCEPTANCE`.

**Scope:** Architecture and specification only. No extractor, model call,
benchmark instance, Dataset v2 mutation, C1 change, Gate 1 work, commit, tag,
or push is included.

## 1. Bounded problem statement

v0.5.0 accepts explicit structured constraints. v0.5.1 may accept a bounded
natural-language request and produce an inspectable candidate
`RetrievalContract` using only the approved registry vocabulary. The goal is
not arbitrary natural-language understanding.

The existing deterministic C1 compiler and runtime remain authoritative for
execution.

## 2. Frozen architecture boundary

```text
Natural-language request
        ↓
semantic / constraint decomposition
        ↓
candidate interpretation
        ↓
deterministic validator
        ↓
user-visible interpretation
        ↓
confirm / edit
        ↓
existing C1 compiler/runtime
        ↓
results + execution evidence
```

No model or generated representation may issue Elasticsearch DSL, execute C1,
or bypass deterministic validation.

## 3. Semantic intent and constraint intent

The interpretation must distinguish:

- **Semantic relevance intent:** the meaning used by Dense retrieval.
- **HARD eligibility constraints:** validated predicates passed to C1.
- **SOFT preferences:** retained as preference/semantic intent; never silently
  converted into hard filters.
- **Exclusions:** explicit negative eligibility predicates.
- **Unsupported/unresolved meaning:** visible and non-executable.

For example, “senior Healthcare experts with Azure experience, at least 20
years, excluding Financial Services” yields semantic Azure AI intent, HARD
Healthcare/experience/seniority constraints, and a Financial Services
exclusion. The example does not define an extraction implementation.

## 4. HARD policy

Candidate HARD semantics are conservative. Explicit mandatory language such as
`must`, `required`, `only`, `at least`, `no less than`, `exclude`, `cannot`,
and `must not` may support a candidate HARD interpretation only when the full
meaning is coherent and registry-supported. Keyword presence alone is not
sufficient. A candidate HARD predicate always requires deterministic
validation and, for the initial release, explicit user confirmation.

## 5. SOFT policy

`prefer`, `preferably`, `ideally`, `nice to have`, `bonus`, `around`, and
`approximately` must not become HARD filters. v0.5.1 represents these as
semantic preferences or suggested/unresolved items. It does not expand C1 into
a soft-ranking architecture.

## 6. Ambiguity and contradiction semantics

Ambiguous polarity, vague numbers, category mappings, scope, implied
constraints, conflicts, and uncertain normalization must remain visible as
`AMBIGUOUS`, `UNRESOLVED`, `SUGGESTED`, or `CONFIRMATION_REQUIRED`; they must
not silently become HARD predicates.

Contradictory candidate contracts (for example `>=20` and `<10`, Healthcare
only while excluding Healthcare, or Senior and Junior only) fail deterministic
validation with a typed contradiction state before retrieval.

## 7. Unsupported and mixed requests

Temporal, employer/client relationship, delivered-for, hands-on, project, and
graph semantics are unsupported in this scope. They must be surfaced rather
than omitted. A mixed request may show a partial candidate preview, but
execution is blocked by default until unsupported items are acknowledged and
the user explicitly confirms the executable supported subset. The UI must never
imply that the whole request was understood.

## 8. Confirmation and editing

Every NL-derived HARD constraint and exclusion requires explicit user
confirmation/edit for the initial release. Existing structured controls remain
the correction surface: users can inspect, change operator/value, remove a
proposed predicate, edit an exclusion, or resolve a supported ambiguity. The
explicit structured mode remains available.

## 9. Candidate versus executable contract

`CandidateInterpretation` is not a `ValidatedRetrievalContract`. A candidate
may contain ambiguity, unsupported items, suggestions, and contradictions.
Only the deterministic validator can create an executable contract.

At architecture level, a candidate interpretation may contain:

- `semantic_query`
- `candidate_constraints`
- `candidate_exclusions`
- `soft_preferences`
- `unsupported_items`
- `unresolved_items`
- `contradictions`
- optional confidence/evidence and source-span metadata
- `interpretation_schema_version`

Incidental implementation fields are deliberately not frozen here.

## 10. Normalization and registry dependency

The authoritative constraint registry is the only capability vocabulary:

`extractor capability ⊆ registry-supported contract capability`.

Display labels and approved aliases may propose canonical values, but unknown
or ambiguous mappings must not invent values. Registry changes require
version-aware interpretation evaluation.

## 11. Interpretation provenance

Interpretation provenance is separate from execution provenance:

```text
Interpretation provenance: NL → candidate interpretation
Execution provenance: validated contract → C1 results
```

The future interpretation record should support source request, extracted
field/operator/value, polarity, support state, ambiguity, normalization,
extractor identity/version, and registry identity. It is designed here but not
implemented in Gate 0.

## 12. Safety model

The asymmetric risk principle is frozen:

`False HARD constraint >> Missed HARD constraint`

A false HARD predicate can remove valid candidates before ranking. A missed HARD
predicate broadens the candidate set and remains visible during confirmation.
Promotion evidence must therefore prioritize false-HARD prevention.

## 13. Evaluation layers and metrics

Evaluation remains separated into:

1. Interpretation: NL → expected candidate contract.
2. Retrieval: validated contract → C1.
3. End-to-end: NL → interpretation → confirmation → C1.

Gate 0 approves metric families, not thresholds:

- field precision/recall;
- operator and normalized-value accuracy;
- exclusion/polarity accuracy;
- unsupported detection precision/recall;
- exact and partial contract match;
- false-HARD and missed-HARD rates;
- contradiction and ambiguity handling accuracy;
- optional HARD/SOFT classification accuracy if retained.

The primary safety metric is **false-HARD constraint rate**: the proportion of
items where the system introduces an executable hard predicate not supported by
the gold interpretation. Missed-HARD rate is reported separately.

## 14. Future benchmark annotation model and strata

Future extraction items should include `query_id`, natural-language request,
semantic intent, expected supported constraints, exclusions, soft/preferences,
unsupported spans, ambiguity and contradiction labels, expected candidate
interpretation, rationale, and annotation confidence/source.

Approved strata are numeric minimum, numeric maximum/range where supported,
industry, role, seniority, location, exclusions, conjunctions,
preference-vs-requirement, semantic-only, ambiguity, contradiction, unknown
category, mixed supported/unsupported, temporal-unsupported, and
relationship-unsupported. No instances are generated in Gate 0.

## 15. Data and corpus relationship

Extraction benchmark data, retrieval corpus, and end-to-end fixtures are
distinct identities. Released v0.5.0 Dataset v2 remains immutable. Gate 1 must
establish auditable identities for any new artifacts, including Healthcare
positive coverage, before end-to-end evaluation.

## 16. Strategy hypothesis

The selected Gate 1/2 hypothesis is:

**conservative hybrid extraction + deterministic schema validation + mandatory
user confirmation**.

Deterministic rules, LLM structured extraction, hybrid rules+LLM, and constrained
structured-output models remain comparison candidates. Future comparison must
consider false-HARD risk, recall, determinism, extensibility, observability,
latency, cost, evaluation complexity, registry awareness, and failure
transparency. No implementation or benchmark is authorized here.

## 17. Model, failure, and no-constraint boundaries

Model output is untrusted candidate interpretation. No model may mutate a
validated contract, discard unsupported intent, issue DSL, or execute C1.

No extractable HARD constraints preserves ordinary C0 semantic retrieval and
may be shown as “No hard constraints detected.” It must not fabricate filters.

Typed interpretation states are:

`INTERPRETED`, `NEEDS_CONFIRMATION`, `AMBIGUOUS`, `PARTIALLY_SUPPORTED`,
`UNSUPPORTED`, `CONTRADICTORY`, and `NO_HARD_CONSTRAINTS`.

## 18. Latency, privacy, and non-goals

Later gates must measure extraction latency, validation latency, confirmation
interaction cost, and model/token cost. No thresholds are frozen here.

External model use requires explicit review of query handling, logging, and data
boundaries. No enterprise compliance infrastructure is designed in Gate 0.

Explicit non-goals are temporal/relationship/evidence reasoning, graph
retrieval, production C2/C3, ANN tuning, arbitrary ontology expansion,
autonomous execution without confirmation, and unrelated inference
infrastructure.

## 19. Gate 1 entry contract

Gate 1 may begin only after founder acceptance of this charter and must assume:

- stable P0 runtime, registry, and execution-provenance identities;
- frozen interpretation semantics, safety model, confirmation policy, metric
  families, annotation model/strata, and non-goals;
- a new versioned extraction schema and benchmark/data plan.

Gate 1 is not started by this document.

## Candidate disposition

Gate 0 is candidate-complete against the charter acceptance criteria. The
Result Package is ready for founder acceptance. No runtime/source
implementation, extractor code, benchmark instance, released-dataset change,
version metadata change, Gate 1 work, commit, tag, or push was started.
