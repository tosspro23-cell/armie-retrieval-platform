# ARMIE Retrieval Platform v0.5 constraint projection design

**Status:** Gate 1.5 design only; no Elasticsearch compiler, index migration,
runtime filtering, or C0–C3 implementation is included.

## 1. Source-of-truth boundary

`datasets/v2.py` Pydantic records are canonical truth. `search_document` and
natural-language summaries are retrieval text, not authoritative constraint
fields. The released v0.4 index and mapping remain immutable.

## 2. Transformation

```text
Dataset v2 records
        ↓ deterministic projection (versioned)
v0.5 constraint projection
        ↓ offline index build
versioned Elasticsearch index
        ↓ later Gate 2 compiler
validated filter DSL
```

The projection must preserve source IDs, provenance/evidence IDs and unknown
state. It must never invent a value from text.

## 3. Versioning and rebuild

Use a new index identity such as
`armie-experts-v0-5-constraints-v1-<dataset-version>`, with an alias changed
only after a complete rebuild and mapping validation. Never alter the v0.4
mapping in place. The projection manifest must include dataset checksum,
schema version, projection version, generator/query/judgement versions and
build timestamp or deterministic marker.

## 4. Proposed canonical fields

| Field | Proposed type | Shape and semantics |
|---|---|---|
| `years_experience` | `integer` | profile aggregate; unknown remains missing |
| `industries` | `keyword[]` | profile aggregate only |
| `roles` | `keyword[]` | profile aggregate only |
| `seniority` | `keyword` + rank metadata | enum `mid/senior/principal`; rank is an explicit derived field, not lexical order |
| `locations` | `keyword[]` | normalized canonical locations |
| `employments` | `nested` | organization, role, industry, start/end, current, evidence IDs |
| `projects` | `nested` | client, role, industry, start/end, delivery level, concepts, evidence IDs |
| `relationships` | `nested` | predicate, object ID/type, valid interval, evidence IDs |
| `evidence` | `nested` | evidence kind, source/object IDs and provenance |

Nested employment, project, relationship and evidence records are required:
flattening them would allow one employment's organization to satisfy another
employment's role or date constraint (a false cross-object match).

## 5. Unknown and temporal semantics

Missing is not a match for a hard constraint. An employment with `end_date=null`
and `current=true` is open-ended; null without that current signal is unknown.
Project intervals are closed. Relationship intervals are optional and null
means unspecified, never all-time. Gate 2 must define overlap explicitly for
`AFTER`, `BEFORE` and `BETWEEN` before compiling temporal filters.

## 6. Relationship and delivery semantics

`worked_at`, `delivered_for` and `advised` remain distinct predicates. The
projection vocabulary uses `worked_at` (matching `RelationshipType`); source
Dataset v2 records currently use `works_at` and require this deterministic
projection normalization only.
Employer
organization and project client are distinct object types. Delivery level and
evidence kind are separate fields: `hands_on` is not equivalent to an arbitrary
skill mention; `advisory` must not satisfy a hands-on requirement.

## 7. Gate 2 compiler eligibility

| Semantic | Gate 2 eligibility | Operators | Reason |
|---|---|---|---|
| `years_experience` | NO | GTE/GT/LTE/LT/BETWEEN | source exists, but 10K projection/completeness evidence is not in checkout |
| `industry` profile | RESTRICTED | EQ/NEQ/IN/NOT_IN | profile aggregate only; no project/employment provenance |
| `role` profile | RESTRICTED | EQ/NEQ/IN/NOT_IN | no interval-specific role proof |
| `seniority` | RESTRICTED | EQ/IN/NOT_IN | enum is defined; rank compilation waits for explicit projection |
| `location` | RESTRICTED | EQ/IN/NOT_IN | normalization/completeness report required |
| employer organization | NO | EQ/IN | nested employer relation required |
| project client | NO | EQ/IN | nested client relation required |
| temporal intervals | NO | AFTER/BEFORE/BETWEEN | overlap semantics and projection not yet compiled |
| relationship predicate/object | NO | EQ/IN | nested object, interval and evidence integrity required |
| delivery/advisory evidence | NO | EQ/IN | evidence-aware nested projection required |

`RESTRICTED` means a future compiler may support only the explicitly listed
profile-level operation after projection validation; it must not silently
fall back to text search. NOT_READY/NO semantics produce the contract's
non-executable unsupported state.

## 8. Migration and non-goals

The projection is offline and rebuildable. It does not introduce a graph
database, change Planner/Retriever contracts, mutate Dataset v2, modify H2,
or implement runtime filtering. Gate 2 must first approve the projection
manifest and field-level completeness evidence, then implement a bounded
compiler against this versioned mapping.
