# Gate 1 — RetrievalContract Foundation review

**Status:** implemented for architecture review; Gate 2 is not started.

## Modules and types

`src/armie_retrieval/contracts.py` adds a frozen, Pydantic v2, backend-neutral
semantic contract layer:

- `RetrievalContract`, `Constraint`, `ConstraintPolicy` and deterministic IDs;
- `ConstraintOperator`, `ConstraintCategory`, `ConstraintStrength`;
- `TemporalConstraint` / `TemporalOperator`;
- `RelationshipConstraint` / `RelationshipType`;
- `ConstraintState` and `CandidateConstraintResult`;
- `ValidationState`, `ValidationIssue`, `ContractValidation` and
  `validate_contract`;
- `CanonicalFieldRegistry` / `FieldSpec`;
- `UnsupportedConstraint`.

The module contains no Elasticsearch syntax, index names, SDK objects,
provider calls or runtime integration.

## Semantics validated

The controlled operators are `EQ`, `NEQ`, `IN`, `NOT_IN`, `GTE`, `GT`, `LTE`,
`LT`, `BETWEEN`, `CONTAINS` and `NOT_CONTAINS`. Shape checks cover ordered
numeric/date values, non-empty collections, valid ranges and scalar values.
Hard constraints, soft preferences and exclusions are separated by immutable
strength checks. Strict policy defaults to `unknown_hard_constraint=exclude`
and `silent_relaxation=false`.

Candidate states `SATISFIED`, `VIOLATED` and `UNKNOWN` are distinct from
contract validation states. Unsupported fields, type mismatch, invalid
operators, ambiguity and contradiction are not candidate violations.

Bounded contradiction checks cover impossible numeric intervals, EQ/NEQ
conflicts and IN/NOT_IN conflicts. This is not a theorem prover.

## Data-model boundary

The readiness audit is in
[`data-model-readiness-audit.md`](data-model-readiness-audit.md). The source
models preserve typed profile, employment, project, relationship, temporal and
evidence data, but the v0.4 Elasticsearch projection does not expose every
field needed for strict enforcement. `years_experience`, seniority ordering
and temporal interval filtering are NOT_READY; industry, role, location,
organization/client and relationship presence are READY_WITH_LIMITATIONS.
No missing-rate estimate was invented.

## Known limitations and unresolved questions before Gate 2

- No compiler or Elasticsearch Query DSL integration exists yet.
- No natural-language extraction exists; unsupported/ambiguous inputs are
  represented but not produced by a parser.
- The field registry is intentionally small and not a Dataset ontology.
- Numeric/date type checks are conservative and do not establish index
  filterability.
- A later data/projection audit must define completeness, null semantics,
  seniority ordering, relation-object filtering and evidence-aware delivery.

## Validation evidence

The focused suite `tests/test_v050_retrieval_contract.py` covers construction,
operator compatibility, policy defaults, hard/soft boundaries, all three
candidate states, serialization, and deterministic contradiction cases. Gate 1
does not modify H1–H4, Workbench behavior, Dataset v1/v2, or runtime outputs.
