# ARMIE Retrieval Platform v0.5.0

## Constraint-Aware Retrieval Systems — Experiment Charter

**Status:** Gate 0 charter; no experiments run
**Control:** released v0.4.0 H2 Dense
**Position:** evaluation-driven, not a pre-registered success claim

## 1. Research question and primary hypothesis

Can deterministic, typed constraint enforcement around the existing Dense
baseline materially improve structured contract satisfaction and hard-negative
resistance without unacceptable degradation in Recall@10, NDCG@5, Precision@5,
MRR or latency?

The primary hypothesis is falsifiable: if correctness gains require unacceptable
recall collapse, relevance loss, extraction error, latency or operational
complexity, the architecture is unsuccessful and must stop or pivot.

## 2. Control and variants

| Variant | Definition | Purpose |
|---|---|---|
| C0 | Existing H2 Dense, no new structured enforcement | Control |
| C1 | Dense plus deterministic native pre-filter | Isolate early eligibility filtering |
| C2 | Dense candidate pool followed by deterministic constraint evaluation and eligible Top-K | Isolate post-retrieval enforcement; report pool size |
| C3 | Reliable indexed constraints as native pre-filters plus post-verification for ambiguous/evidence-dependent conditions | Test hybrid enforcement without assuming it wins |

H1/H3/H4 may remain reference profiles, but the experimental axis must not
change embedding, fusion, reranking, Dataset v1/v2 or released candidate
boundaries at the same time as constraint enforcement.

## 3. Constraint categories

The benchmark must cover numeric, categorical, location/discipline where
canonical, role/seniority, temporal, prohibited/negative, unknown,
contradictory, and typed relationship cases. Relationships begin with
`worked_at`, `delivered_for`, `advised`, `managed` and `partnered_with`.

The benchmark must distinguish hard constraints, soft preferences, exclusions,
temporal conditions and evidence-dependent relations. Missing evidence is
`UNKNOWN`, not positive evidence.

Dataset v2 continuity is mandatory: later constraint-focused queries and
judgements use the same 10,000-profile corpus and a new versioned benchmark
extension. They do not mutate the released v0.4.0 103 Gold / 17 Silver set.
Existing v0.4 queries remain regression/reference cases. Small deterministic
fixtures and stratified slices are permitted before Gate 6; the full C0–C3
comparison belongs to Gate 6.

## 4. Query-contract evaluation

Every case pairs a natural query with an expected RetrievalContract and a
predicted contract. Evaluate:

- constraint detection and field selection;
- operator correctness and value extraction;
- hard versus soft classification;
- negative and temporal extraction;
- contradiction detection;
- unsupported-condition handling;
- exact contract match and field-level precision/recall.

The validator must emit `INVALID_CONTRACT` for contradictions such as
`years_experience >= 20 AND years_experience < 10`, rather than silently
executing or relaxing them. Unsupported fields must be distinct from unknown
candidate values, extraction ambiguity and an actual violation.

## 5. Retrieval and constraint metrics

Preserve standard relevance metrics: NDCG@5, Precision@5, Recall@10, MRR and
Grade-3 Hit@5. Add:

- **Required Constraint Satisfaction@5:** Top-5 fraction satisfying all hard
  required constraints.
- **Constraint Violation@5:** Top-5 fraction with at least one known hard
  violation.
- **Prohibited Constraint Violation@5:** Top-5 fraction violating an explicit
  negative requirement.
- **Unknown Constraint Rate@5:** Top-5 fraction with an unverifiable hard
  requirement.
- **True Hard-Negative Intrusion@5:** preserved structured near-miss rate,
  separate from ordinary negatives.
- **Eligible Recall@K:** recall against candidates both relevant and
  contract-eligible where Gold structure permits.

Metrics must retain their denominator, tier, profile and candidate boundary.
Constraint metrics do not replace standard relevance metrics.

## 6. Evaluation questions

The benchmark must answer:

1. Does constraint-aware retrieval improve required satisfaction?
2. Does it reduce prohibited violations and true hard-negative intrusion?
3. What happens to Recall@10, NDCG@5, Precision@5 and MRR?
4. What is the latency cost and how does it vary by constraint class?
5. Which classes benefit from pre-filter versus post-filter?
6. How often is `UNKNOWN` returned?
7. How often is the predicted contract invalid or unsupported?
8. Does deterministic verification agree with Gold structured truth?

## 7. Benchmark design principles

Use stratified cases for numeric, categorical, role/seniority, temporal,
negative, unknown, contradiction and relationship conditions. Preserve Gold /
Silver isolation and the v0.4.0 synthetic limitation. Do not rewrite Dataset v1,
Dataset v2 or the released v0.4.0 benchmark. A future v0.5 benchmark may be a
versioned extension only after the data-model audit and explicit gate approval.

The motivating near-miss is an expert who is semantically relevant but has
8–9 years or unknown experience when the contract requires 20+. Hard negatives
must be structured near-misses (wrong relation, advisory-only, outside window,
missing required skill or prohibited violation), not all unrelated Grade-0
rows.

## 8. Unknown, contradiction and unsupported handling

Constraint states are `SATISFIED`, `VIOLATED` and `UNKNOWN`. Strict policy
excludes `UNKNOWN` from hard-constraint eligibility but preserves it in
evidence. Contradictions produce `INVALID_CONTRACT`; unsupported conditions
produce an explicit unsupported/unverifiable state. No silent relaxation is
allowed. Soft preferences cannot become hard exclusions.

## 9. Statistical comparison plan

Compare C0–C3 on the same versioned query cases, candidate boundaries and
execution environment. Report paired per-query deltas, win/tie/loss where
appropriate, distributions and confidence intervals when sample size supports
them. Do not claim significance for small strata; record power and sample-size
limitations. Pre-register success/guardrail thresholds at the benchmark-design
gate rather than fabricating values in Gate 0.

## 10. Latency measurement

Measure retrieval, native filtering, post-verification, eligible Top-K assembly
and end-to-end latency separately. Report cold/warm state, p50/p95, profile,
constraint category and candidate-pool size. End-to-end must not be lower than
the included stage timings for the same execution sample.

## 11. Success and failure criteria

Primary success requires material improvement in Required Constraint
Satisfaction@5, Prohibited Constraint Violation@5 and True Hard-Negative
Intrusion@5 over C0. Guardrails require no unacceptable degradation in
Recall@10, NDCG@5, Precision@5, MRR or latency. The numeric thresholds are
`TBD at benchmark-design gate`; they must be justified from v0.4 evidence,
sample size and product tolerance before execution.

Failure includes extraction too inaccurate for hard constraints, high false
exclusion from pre-filtering, impractical post-filter latency, unacceptable
eligible recall loss, non-deterministic verification, or a data-model redesign
larger than the release scope. A failed hypothesis is a valid result.

## 12. Evidence required before architectural promotion

Promotion requires a versioned benchmark and manifest, contract extraction
audit, schema-readiness evidence, deterministic compiler tests, C0–C3 paired
results, constraint and standard relevance metrics with denominators, latency
breakdown, unknown/unsupported/contradiction rates, evidence samples,
regression results, and explicit limitation statements. No component becomes a
default merely because it has been implemented.

## 13. Future Workbench target

Gate 8 may expose natural query, parsed contract, C0/C1/C2/C3 strategy,
pre/post-filter allocation, candidate eligibility, constraint evidence,
unknown state, reason codes, diagnostics and separate relevance/correctness/
latency metrics. Backend truth must drive presentation; the Workbench is not an
Elasticsearch DSL console.

## 14. Proposed development gates

| Gate | Scope | Stop condition |
|---|---|---|
| Gate 0 | Architecture decision and experiment charter | Complete only after boundaries, metrics and risks are reviewed |
| Gate 1 | RetrievalContract types, operators, validation, reason codes and three-valued tests | Stop if schema semantics are not stable |
| Gate 2 | Deterministic Elasticsearch constraint compiler and DSL tests | Stop if mappings cannot express required semantics safely |
| Gate 3 | C1 native pre-filter integrated with H2 | Stop on high false exclusion or recall loss |
| Gate 4 | C2 controlled candidate-pool post-filter | Stop on impractical pool/latency cost |
| Gate 5 | C3 hybrid enforcement, only if C1/C2 evidence supports it | Stop if partitioning conditions is not deterministic |
| Gate 6 | Versioned stratified constraint benchmark and C0–C3 comparison | Stop if metrics or labels are not auditable |
| Gate 7 | Bounded typed relationship experiment, no general graph | Stop if relation data requires a larger model redesign |
| Gate 8 | Workbench constraint inspection and browser acceptance | Stop if UI diverges from backend contract truth |
| Gate 9 | Release readiness, docs, packaging and full regression | Stop if evidence boundaries or identity are inconsistent |

Gates may stop, pivot or be re-scoped when evidence invalidates the hypothesis;
they are not a promise that every gate will execute unchanged.

## 15. Non-goals

This charter does not authorize a general knowledge graph, GraphRAG redesign,
new embedding or reranker, fine-tuning, autonomous agent workflow,
authentication, tenancy, cloud infrastructure redesign, production SaaS,
universal natural-language-to-DSL generation, automatic silent relaxation or
arbitrary user-defined DSL execution.
