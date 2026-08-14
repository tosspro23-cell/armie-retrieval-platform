# ARMIE Retrieval Platform v0.5.0

## Constraint-Aware Retrieval Systems — Architecture Decision

**Status:** Gate 0 planning decision; not implemented
**Scope:** architecture and experiment charter only
**Release boundary:** v0.4.0 remains immutable

## 1. Problem statement

v0.4.0 established H2 Dense as the strongest practical default candidate on
the controlled Dataset v2 distribution, but also showed that semantic
relevance does not guarantee business-contract eligibility. Employer/client
relations, delivery versus mention, temporal windows, role/seniority and
prohibited conditions can remain unsatisfied even when a candidate is
semantically close. The next question is therefore not “which larger ranker?”
but whether typed, deterministic constraint enforcement around H2 improves
contract correctness without unacceptable relevance, recall or latency cost.

## 2. v0.4.0 evidence boundary

The evidence is the released Dataset v2 benchmark: 10,000 profiles, 120
queries, 103 Gold and 17 Silver, with frozen H1–H4 boundaries. H2 Gold NDCG@5
was `0.7569` versus H1 `0.6054`; H3 was `0.7594` and H4 `0.7596`. H2 remained
the practical default candidate, while H3 added only a small aggregate gain
and H4 added substantial local latency. Gold is an independent structured
audit, Silver is rule-assisted, and the corpus is a **controlled synthetic
relevance benchmark**, not natural expert-network ground truth.

The v0.4.0 closeout also records that structured relationship, temporal,
negative and role semantics are not fully handled by ranking alone. These are
motivating observations, not v0.5.0 results.

### Dataset v2 corpus continuity

Dataset v2 remains the primary v0.5.0 corpus. The 10,000 profiles and released
v0.4.0 benchmark are immutable. A later versioned constraint-focused
query/judgement extension may run against the same corpus, but must not replace
or mutate the released 103 Gold / 17 Silver benchmark. Existing v0.4 queries
remain regression/reference cases; additional slices may cover numeric,
categorical, role/seniority, temporal, negative, UNKNOWN, contradiction and
relationship near-miss cases. Gates 1–5 may use small deterministic fixtures
and stratified slices; Gate 6 is the formal full C0–C3 benchmark and Gate 9 is
release-level reproducibility/regression.

## 3. Architecture hypothesis

The primary falsifiable hypothesis is:

> Compared with the v0.4.0 H2 Dense baseline, constraint-aware retrieval can
> materially improve structured contract satisfaction and hard-negative
> resistance while preserving acceptable retrieval relevance, recall and
> latency.

The hypothesis fails if correctness improves only through unacceptable recall
collapse, relevance degradation, latency, extraction error or operational
complexity. No C1, C2 or C3 variant is a winner before experiment evidence.

## 4. Control baseline and boundaries

The main control is the released **H2 — Dense** profile. It remains C0 in the
experiment and is not renamed H5/H6/H7. H1, H3 and H4 remain reference profiles
only. v0.5.0 does not change embeddings, rerankers, Dataset v1/v2, candidate
boundaries or the released benchmark.

The high-level target flow is:

```text
Natural Language Query
        ↓
Query Understanding
        ↓
Typed Retrieval Contract
        ↓
Contract Validation
        ↓
Constraint Policy
        ↓
Retrieval Planner
        ↓
Elasticsearch Native Execution
        ↓
Constraint Verification
        ↓
Ranking / Eligible Top-K
        ↓
Evidence & Provenance
        ↓
Evaluation & Governance
```

Query understanding may propose intent. Trusted application code validates and
compiles it. An extractor never directly emits final Elasticsearch DSL.

## 5. Accepted architecture decisions

### ADR-1 — Hard constraints and soft preferences are distinct

Hard constraints determine eligibility. A failed hard constraint makes a
candidate ineligible. Soft preferences may affect ranking or explanation but
never become silent hard exclusions. Examples include `years_experience >= 20`
as hard, and “preferably based in Europe” as soft.

### ADR-2 — Unknown is a first-class state

Every constraint evaluation uses `SATISFIED`, `VIOLATED` or `UNKNOWN`. Under
the default `strict` policy, `UNKNOWN` does not satisfy a hard constraint and
is excluded from eligible Top-K, while remaining visible in diagnostics.

### ADR-3 — Pre-filter and post-filter are experimental strategies

C1 pre-filtering may be efficient but can over-exclude after extraction or
mapping errors. C2 post-filtering protects candidate recall but may require a
larger pool and more latency. C3 combines reliable native filters with
deterministic verification for evidence-dependent conditions. No strategy is
preselected as the winner.

### ADR-4 — Initial constraint scope is bounded

The first scope covers numeric, categorical, role/seniority, temporal,
negative/prohibited and typed relationship conditions. Initial relationship
types are `worked_at`, `delivered_for`, `advised`, `managed` and
`partnered_with`, optionally with an interval and provenance. This is not a
general-purpose knowledge graph or GraphRAG redesign.

### ADR-5 — Hybrid extraction plus deterministic compiler

Rule/model-assisted extraction proposes a typed contract. Schema, ontology,
type, contradiction and policy validation precede a deterministic compiler.
Only validated ARMIE operators compile to backend queries; query-understanding
components never receive arbitrary Elasticsearch DSL authority.

### ADR-6 — No silent hard-constraint relaxation

If only three candidates satisfy a hard contract, return three eligible
candidates. Do not add fifteen-year or unknown candidates to fill Top-K.
Any future relaxation must be explicit, observable, user-visible and
auditable; silent relaxation is prohibited in the v0.5.0 core path.

## 6. RetrievalContract boundary

The contract is a backend-independent semantic object. Its concepts include:

```yaml
semantic_query:
  text: "energy engineer"
hard_constraints: []
soft_preferences: []
exclusions: []
temporal_constraints: []
relationship_constraints: []
policy:
  mode: strict
  unknown_hard_constraint: exclude
  silent_relaxation: false
```

The exact serialization is intentionally not frozen in Gate 0. Semantic
concepts, ownership, and state transitions are frozen; implementation syntax
must follow existing ARMIE type conventions at Gate 1.

The initial controlled operator vocabulary is `eq`, `neq`, `in`, `not_in`,
`gte`, `gt`, `lte`, `lt`, `between`, `contains` and `not_contains`. Arbitrary
backend operators are not exposed to query understanding.

## 7. Elasticsearch responsibility boundary

```text
ARMIE = semantics + policy + planning + governance
Elasticsearch = retrieval/filter execution
```

Elasticsearch may execute supported native primitives such as kNN filters,
`bool.filter`, `must`, `must_not`, `term`, `terms`, `range` and justified
nested filters. ARMIE owns intent extraction, validation, unknown semantics,
hard/soft policy, planning, deterministic DSL compilation, verification,
evidence and evaluation. ARMIE does not reimplement Elasticsearch filtering.

## 8. Constraint compiler boundary

```text
RetrievalContract → ConstraintCompiler → BackendQueryPlan
```

The later Elasticsearch implementation is an `ElasticsearchConstraintCompiler`.
The semantic contract does not contain Elasticsearch syntax, index names, SDK
calls or provider details. No second provider is planned in v0.5.0; the
boundary preserves future portability without creating a multi-backend
feature now.

## 9. Verification model

Filtering is not sufficient for auditability. Each candidate should eventually
carry a result for each constraint:

```text
constraint_id
status: SATISFIED | VIOLATED | UNKNOWN
canonical_field
expected_operator
expected_value
observed_value
evidence
source
reason_code
```

The system must be able to explain inclusion, exclusion and unverifiable
requirements. Rejected candidates need not appear in the primary Workbench,
but their diagnostic evidence must remain reconstructable.

## 10. Auditability requirements

An execution must eventually reconstruct the original query, parsed contract
and version, policy version, planner strategy, compiled backend filter,
candidate stage, constraint decisions, observed values, evidence, exclusion
reason, final result set and timing. Internal or sensitive details should not
be exposed unnecessarily in the primary UI.

## 11. Canonical motivating failure

```text
Intent: engineers in a target industry with >20 years of experience
Observed v0.4 pattern: semantically relevant candidates with ~8–9 years or
unknown experience may rank ahead of candidates satisfying 20+ years
Interpretation: semantic relevance is high, but eligibility is violated
```

This is a test shape, not a claim of a tracked production metric.

## 12. Relationship strategy

Use a bounded typed relation model: expert subject, typed relation, organization
or project object, optional interval and provenance. First test employer/client
and delivery/mention distinctions with typed projection and verification.
Do not create Neo4j, RDF or general graph infrastructure in the core plan.

## 13. Deferred capabilities and non-goals

The initial scope excludes a general knowledge graph, GraphRAG redesign, new
embeddings or rerankers, fine-tuning, autonomous agents, authentication,
tenancy, cloud redesign, production SaaS, universal natural-language-to-DSL
generation, arbitrary user DSL execution and automatic silent relaxation.
Natural-data validation remains strategically important but is a later pilot,
not the primary runtime theme. Selective reranking remains a deferred
hypothesis, not a Gate 0 implementation commitment.

## 14. Risks and stop/pivot conditions

Stop or pivot if extraction is unreliable for hard constraints, canonical
fields are too incomplete, strict filtering causes unacceptable eligible-recall
loss, pre-filtering produces high false exclusion, post-filter pools require
impractical latency, verification cannot be deterministic, or relationship
semantics require a data-model redesign larger than this release.

## 15. Data-model audit before Gate 1

Before implementation, audit every target constraint for canonical source field,
type, completeness/null rate, ambiguity, derivation method, Elasticsearch
mapping, filterability and evidence provenance. In particular, determine
whether `years_experience` exists as a canonical numeric field, whether it is
total or domain experience, how it is derived, its missing-value rate and
whether it is safe as a hard filter. Do not assume Dataset v2 fields are all
ready for strict enforcement.

## 16. Architecture decision matrix

| Direction | Contract correctness | Relevance preservation | Recall risk | Latency | Observability | Auditability | Complexity | Portability |
|---|---|---|---|---|---|---|---|---|
| No structured enforcement | Low | Current H2 reference | Low relative to H2 | Current H2 | Low | Low | Low | High |
| Pre-filter | Potentially high | Sensitive to extraction/mapping | Medium–high | Potentially low | Medium | High | Medium | Medium |
| Post-filter | High for verified fields | Candidate-pool dependent | Medium | Medium–high | High | High | Medium | High |
| Hybrid enforcement | Potentially highest | Must partition conditions correctly | Medium | Medium | High | High | High | Medium |

The matrix is a decision aid, not a winner declaration. Evidence from later
gates must promote or reject each direction.
