# ARMIE Retrieval Platform v0.4.0 Engineering Specification

## Expert Discovery Relevance Engineering Foundation

**Status:** Implementation draft
**Target:** `v0.4.0`
**Baseline:** `v0.3.0 — Interactive Retrieval Workbench`
**Mode:** Local-first
**Primary backend:** Elasticsearch
**Reference domain:** Expert Discovery

---

## 1. Purpose

v0.3.0 established a browser-validated retrieval workbench with declarative planning, a capability registry, dense/sparse/graph retrieval, RRF fusion, metadata and BGE Cross-Encoder reranking, trace-derived evidence, deterministic verification, metrics, and Query Lab comparison.

v0.4.0 moves the platform from **mechanism validation** to **relevance engineering**.

The release shall establish:

- a versioned Expert Discovery domain model;
- a reproducible dataset of approximately 10,000 expert records;
- approximately 120 labelled benchmark queries;
- 0–3 graded relevance judgements;
- explicit query and failure taxonomies;
- Elasticsearch BM25 and dense retrieval;
- FAISS versus Elasticsearch dense comparison;
- ARMIE-controlled hybrid fusion and Cross-Encoder reranking;
- category-level quality, latency, and failure analysis;
- reproducible experiment manifests and architecture decisions.

Core research question:

> Can ARMIE evaluate, explain, and govern retrieval quality across lexical, dense, hybrid, and reranked search strategies in an Expert Discovery domain?

---

## 2. Goals

v0.4.0 shall answer:

1. Which query classes are best served by BM25?
2. Which classes benefit from dense semantic retrieval?
3. Does hybrid retrieval improve Recall@K or NDCG@K consistently?
4. Does BGE Cross-Encoder reranking justify its latency?
5. How does Elasticsearch dense retrieval differ from FAISS?
6. Which failures come from data, indexing, retrieval, fusion, reranking, planning, or labels?
7. Which failures justify future Knowledge Graph work?
8. Which queries do not require an LLM planner?
9. Can every benchmark result be reproduced and inspected?

---

## 3. Non-goals

This release shall not implement:

- hosted multi-tenant SaaS;
- authentication or cloud persistence;
- GCP production deployment;
- Kubernetes;
- high-concurrency production SLOs;
- a complete Knowledge Graph;
- recommendation systems;
- learning-to-rank;
- autonomous online learning;
- automated production policy promotion;
- distributed FAISS;
- full index-management UI;
- end-user file upload.

---

## 4. Architecture invariants

The following v0.3.0 properties must remain intact:

- Planner output is declarative.
- `RetrievalPlan` is immutable after planning.
- Runtime executes rather than rewrites the plan.
- Provider selection is explicit.
- Requested and actual providers are traceable.
- Fallback is controlled and observable.
- Evaluation is observational.
- Evidence is derived from trace and indexed data.
- Verification is deterministic.
- Hidden chain-of-thought is never exposed.
- Workbench remains a projection of the shared runtime.
- Score values retain stage, provider, and scale semantics.
- Browser acceptance tests remain release gates.

Target flow:

```text
Dataset
→ Validation
→ Elasticsearch / FAISS indexing
→ Capability Registry
→ Planner
→ RetrievalPlan
→ Retrieval Runtime
→ BM25 / Dense
→ RRF Fusion
→ Metadata or BGE Reranking
→ Evaluation
→ Evidence / Verification
→ Query Lab / Reports
```

---

## 5. Engineering principles

### Evaluation-driven

No profile may be described as better without benchmark evidence.

### Reproducible

Every run must identify:

- dataset version and checksum;
- query-set and judgement version;
- index version;
- embedding model;
- backend version;
- retrieval profile;
- planner and reranker;
- code commit;
- runtime configuration;
- experiment fingerprint.

### Control plane versus data plane

ARMIE remains the control, evaluation, and governance plane. Elasticsearch and FAISS remain retrieval data planes.

### Typed contracts

Dataset records, queries, judgements, manifests, traces, metrics, and reports must use typed schemas.

### Controlled evolution

No provider, model, or policy is promoted automatically.

---

## 6. Expert Discovery domain model

Primary searchable entity: `ExpertProfile`.

Required fields:

```python
class ExpertProfile(BaseModel):
    expert_id: str
    display_name: str
    headline: str
    summary: str
    skills: list[str]
    industries: list[str]
    technologies: list[str]
    roles: list[str]
    seniority: str | None
    employers: list[EmploymentRecord]
    projects: list[ProjectRecord]
    locations: list[str]
    languages: list[str]
    years_experience: int | None
    certifications: list[str]
    availability_status: str | None
    source_type: str
    source_provenance: list[SourceReference]
    synthetic_fields: list[str]
    schema_version: str
```

`EmploymentRecord` shall include organization, role, years, industry, and description.

`ProjectRecord` shall include project ID, title, client type, industry, role, technologies, skills, description, dates, and delivery evidence.

Every field must identify whether it is sourced, transformed, manually authored, generated, or inferred. No real private or sensitive personal data is allowed.

A deterministic, versioned `search_document` projection must preserve field boundaries rather than flattening all content without structure.

---

## 7. Dataset design

### Target

- Default: 10,000 records.
- Acceptable range: 8,000–15,000.
- Stable IDs.
- Deterministic seed.
- Versioned manifest and checksum.

### Composition

Use a mixed strategy:

- licence-safe realistic text;
- controlled synthetic structured attributes;
- lexical and paraphrase variation;
- explicit hard negatives;
- near duplicates;
- incomplete and noisy profiles;
- verbose and sparse profiles.

Required slices include:

- exact matches;
- semantic paraphrases;
- skill-only false positives;
- industry-only false positives;
- employer-versus-client ambiguity;
- technology mention without delivery evidence;
- stale experience;
- adjacent industry;
- incorrect seniority or geography;
- partial multi-constraint matches.

Dataset manifest must include dataset ID/version, schema version, record count, seed, generator version, licences, projection version, timestamp, and checksum.

Validation must fail on duplicate IDs, broken references, invalid fields or dates, empty search projections, invalid judgement references, invalid grades, insufficient taxonomy coverage, or non-deterministic builds.

---

## 8. Query taxonomy

Approximately 120 labelled queries:

| Category | Target |
|---|---:|
| Exact skill | 15 |
| Skill + industry | 15 |
| Delivery/project experience | 15 |
| Organization experience | 10 |
| Seniority/role | 10 |
| Multi-constraint | 20 |
| Semantic paraphrase | 15 |
| Hard negative/ambiguity | 10 |
| Temporal constraint | 5 |
| Negative constraint | 5 |

Query contract:

```python
class BenchmarkQuery(BaseModel):
    query_id: str
    query_text: str
    category: QueryCategory
    intent_summary: str
    required_constraints: list[QueryConstraint]
    optional_constraints: list[QueryConstraint]
    prohibited_constraints: list[QueryConstraint]
    expected_retrieval_signals: list[str]
    judgement_set_id: str
    query_set_version: str
```

Controlled ambiguity cases must include:

- worked for an organization versus delivered work for it;
- mentioned a technology versus implemented it;
- broad industry adjacency versus direct experience.

---

## 9. Relevance contract

Grades:

```text
3 — Highly relevant:
    Satisfies all core constraints with direct evidence.

2 — Relevant:
    Satisfies main constraints but lacks a secondary condition
    or has weaker evidence.

1 — Partially relevant:
    Adjacent or incomplete experience.

0 — Not relevant:
    Fails a core constraint, contradicts the query,
    or matches a prohibited condition.
```

Each query must declare core, secondary, and prohibited constraints.

Evidence hierarchy:

1. explicit project delivery evidence;
2. structured project fields;
3. employment evidence;
4. skill metadata;
5. summary mention;
6. inferred adjacency.

A skill mention does not equal delivery experience. Employment at a company does not equal consulting for that company.

Judgement schema must include query ID, expert ID, grade, matched/missing/violated constraints, evidence references, rationale codes, reviewer, review status, and version.

Default workflow:

```text
Rule-assisted draft
→ Manual review
→ Explicit correction
→ Versioned judgement set
```

LLMs may assist but cannot be the unreviewed source of truth.

---

## 10. Elasticsearch environment

Run Elasticsearch locally through Docker Compose. Pin the exact version.

Startup health must expose:

- Elasticsearch reachability and version;
- cluster health;
- expected index and mapping version;
- document count;
- ARMIE package source path and version;
- repository commit;
- API and frontend version.

Endpoints and credentials must use environment variables. No secrets or Elasticsearch data volumes are committed.

---

## 11. Elasticsearch index design

Use versioned indices and aliases:

```text
armie-experts-v1-<build_id>
armie-experts-read
armie-experts-write
```

Recommended field types:

- `keyword` for normalized skills, technologies, industries, roles, and locations;
- `text` for headline, summary, and project descriptions;
- `nested` for projects and employment when needed;
- `dense_vector` for embeddings;
- dates or integers for time fields.

Initial analyzers:

- standard English analysis;
- lowercase normalization;
- keyword subfields;
- versioned controlled synonyms;
- optional stemming only when benchmark evidence supports it.

Initial BM25 boosts are experimental defaults:

| Field | Boost |
|---|---:|
| skills.keyword | 4.0 |
| technologies.keyword | 4.0 |
| projects.title | 3.0 |
| projects.description | 2.5 |
| industries.keyword | 2.0 |
| roles.keyword | 2.0 |
| headline | 1.5 |
| summary | 1.0 |

The dense field must record dimensions, similarity metric, embedding model/version, and normalization policy.

FAISS and Elasticsearch comparisons should use the same document projection and embedding model.

---

## 12. Indexing pipeline

```text
Load
→ Validate
→ Build search projection
→ Generate embeddings
→ Build Elasticsearch documents
→ Bulk index
→ Validate mapping/count
→ Build FAISS index
→ Emit index manifest
```

Requirements:

- deterministic and idempotent;
- bounded bulk batches;
- transient retries;
- permanent partial-write failure;
- rejected-document report;
- separate indexing and embedding latency;
- full rebuild and alias switch;
- explicit index deletion command.

Index manifest must include dataset checksum, mapping/projection versions, embedding model and dimensions, document count, Elasticsearch version, FAISS index type, timestamp, and fingerprint.

Incremental updates are optional, not a release gate.

---

## 13. Capability Registry

Registry entries must represent capability and provider metadata.

Required providers:

- `ElasticsearchBM25Retriever`
- `ElasticsearchDenseRetriever`
- existing `FaissDenseRetriever`

Entries should include capability, implementation, index identity, supported filters, candidate limits, health, model/metric, and mapping version.

The Planner requests capabilities, not backend-specific implementation details. Benchmark profiles bind capabilities to providers explicitly.

---

## 14. Retriever requirements

### Elasticsearch BM25

Must support:

- structured query construction;
- field boosts;
- metadata filters;
- candidate counts;
- provider/index identity;
- backend latency;
- query fingerprint;
- optional bounded `explain`;
- score type `bm25_score`.

### Elasticsearch Dense

Must support:

- kNN retrieval;
- explicit `k` and candidate breadth;
- compatible embedding configuration;
- metadata filters where supported;
- provider/index identity;
- backend-specific dense score semantics.

### FAISS Dense

Retain existing implementation. Primary comparison should use normalized vectors and `IndexFlatIP` as an exact baseline where feasible.

ANN HNSW/IVF/PQ tuning is out of scope for the main release.

The existing local sparse retriever may remain for regression compatibility but must not be presented as equivalent to Elasticsearch BM25 without evidence.

---

## 15. Benchmark profiles

Required profiles:

### P1 — Elasticsearch BM25

```text
Rule Planner → Elasticsearch BM25 → Metadata Boost → Top-K
```

### P2 — FAISS Dense

```text
Rule Planner → FAISS Dense → Metadata Boost → Top-K
```

### P3 — Elasticsearch Dense

```text
Rule Planner → Elasticsearch Dense → Metadata Boost → Top-K
```

### P4 — Elasticsearch BM25 + FAISS Dense

```text
Rule Planner
→ Elasticsearch BM25 + FAISS Dense
→ ARMIE RRF
→ Metadata Boost
→ Top-K
```

### P5 — Elasticsearch BM25 + Elasticsearch Dense

```text
Rule Planner
→ Elasticsearch BM25 + Elasticsearch Dense
→ ARMIE RRF
→ Metadata Boost
→ Top-K
```

### P6 — Hybrid + BGE Cross-Encoder

```text
Rule Planner
→ BM25 + selected Dense provider
→ ARMIE RRF
→ BGE Cross-Encoder
→ Top-K
```

An Ollama-planned profile may remain diagnostic but shall not replace deterministic comparisons.

---

## 16. Candidate boundaries

Explicit stages:

```text
retrieval_candidate_k
→ fusion_candidate_k
→ rerank_candidate_k
→ final_top_k
```

Recommended defaults:

```text
100 → 100 → 30 → 5
```

Every value is configurable and recorded. No stage may silently expand or truncate candidates.

---

## 17. Fusion and score governance

ARMIE RRF remains the primary cross-provider fusion method.

Record per candidate:

- source provider;
- source rank;
- source score and semantic;
- RRF contribution;
- total fused score;
- fusion rank;
- deduplication result.

BM25, cosine similarity, inner product, RRF, metadata scores, and Cross-Encoder scores must never be presented as directly comparable.

---

## 18. Reranking

Retain:

- deterministic metadata boost as baseline;
- bounded BGE Cross-Encoder as model-enhanced reranker;
- explicit model and provider identity;
- controlled fallback;
- macOS process isolation where required.

Trace must include model-load, inference, and total reranking latency; pre/post ranks; rank change; final Top-K membership; and fallback reason.

The report must quantify quality gain versus latency cost globally and by query category.

---

## 19. Evaluation

Primary metrics:

- `NDCG@5`
- `Recall@10`
- `Precision@5`
- `MRR`

Diagnostics:

- NDCG@10 and Recall@5;
- first relevant rank;
- zero-result rate;
- grade-3 hit rate;
- hard-negative intrusion;
- prohibited-constraint violations;
- required-constraint satisfaction;
- Top-K overlap and Jaccard;
- rank movement;
- source contribution;
- p50/p95 latency;
- stage latency;
- indexing and embedding time;
- index size.

Report metrics globally and by category, profile, constraint type, difficulty, and labelled slice.

Include per-query deltas and profile win/tie/loss counts. Bootstrap confidence intervals are recommended where practical. Do not make unsupported statistical-significance claims.

---

## 20. Failure taxonomy

Required codes:

- `dataset_missing_evidence`
- `schema_modelling_gap`
- `lexical_mismatch`
- `semantic_false_positive`
- `filter_failure`
- `constraint_violation`
- `employer_client_ambiguity`
- `delivery_mention_ambiguity`
- `fusion_displacement`
- `reranker_regression`
- `candidate_pool_miss`
- `stale_experience`
- `near_duplicate`
- `judgement_gap`
- `planner_routing_error`
- `backend_inconsistency`
- `graph_relationship_needed`

A query may have multiple codes. Reports must distinguish retrieval failure from judgement failure.

---

## 21. Evidence and Verification

For each final result, Evidence must expose:

- matched fields and terms;
- semantic source;
- source rank and score semantic;
- matched, missing, and violated constraints;
- project/employment evidence;
- fusion contribution;
- reranker movement;
- final rank.

No evidence may invent facts absent from the indexed record.

Verification must add:

- dataset/index/query/judgement version consistency;
- provider and index identity;
- embedding compatibility;
- metric eligibility;
- candidate-count and rank consistency;
- prohibited-constraint checks;
- judgement reference integrity;
- run fingerprint;
- score-semantic integrity.

Verification remains observational and cannot rewrite results.

---

## 22. Query Lab requirements

Required additions:

- query category and difficulty;
- core and prohibited constraints;
- judgement and benchmark version;
- result relevance grades;
- metric and latency deltas;
- backend/provider identity;
- false-positive and false-negative inspection;
- missing grade-3 candidates;
- hard-negative intrusions;
- failure-stage classification;
- category summary for NDCG, Recall, Precision, MRR, and p50/p95.

Do not redesign the entire Workbench. Only changes necessary for relevance inspection are in scope.

---

## 23. API and CLI

Recommended API:

```text
GET  /api/v1/datasets
GET  /api/v1/datasets/{id}
GET  /api/v1/benchmarks
GET  /api/v1/benchmarks/{id}/queries
POST /api/v1/benchmarks/{id}/runs
GET  /api/v1/benchmark-runs/{id}
GET  /api/v1/benchmark-runs/{id}/report
GET  /api/v1/benchmark-runs/{id}/failures
GET  /api/v1/indexes
POST /api/v1/indexes/build
GET  /api/v1/indexes/{id}/status
```

Recommended CLI:

```bash
armie dataset build --config configs/datasets/expert_discovery_v1.yaml
armie dataset validate --dataset data/expert_discovery_v1
armie index build --backend elasticsearch --dataset expert-discovery-v1
armie index build --backend faiss --dataset expert-discovery-v1
armie benchmark validate --benchmark benchmarks/expert_discovery_v1
armie benchmark run --profiles es-bm25 faiss-dense es-dense hybrid-bge
armie benchmark report --run-id <id>
```

Long-running orchestration may remain CLI-based if adding an API job system would inflate scope.

---

## 24. Experiment manifest and reports

Every run must emit a machine-readable manifest containing:

- run ID and commit;
- dataset checksum;
- query and judgement versions;
- index manifest;
- profile, planner, retrievers, fusion, and reranker;
- candidate boundaries;
- environment versions;
- fingerprint.

Outputs:

1. JSON report with per-run, aggregate, category, query, latency, failure, and verification data.
2. Markdown report with executive summary, benchmark design, profile definitions, comparisons, failures, decisions, limitations, and next-step recommendation.
3. ADR answering when ARMIE should use BM25, Elasticsearch Dense, FAISS Dense, Hybrid RRF, and Cross-Encoder reranking.

---

## 25. Testing

### Unit

- schemas and validation;
- projection builder;
- metrics;
- failure classification;
- fingerprints;
- registry bindings;
- score semantics;
- RRF calculations.

### Dataset integrity

- deterministic generation;
- record and category counts;
- IDs and references;
- hard negatives;
- judgement grades and coverage.

### Elasticsearch integration

- Docker health;
- mapping and aliases;
- bulk indexing;
- BM25, dense, and filtered queries;
- trace data;
- document-count integrity.

### FAISS integration

- deterministic build;
- vector count;
- metric compatibility;
- ID mapping;
- exact-baseline execution.

### Runtime

- provider/profile selection;
- plan immutability;
- explicit fallback;
- candidate boundaries;
- fusion/reranker trace;
- metric eligibility.

### API/frontend

- non-empty required DTOs;
- benchmark and report endpoints;
- grades, metrics, failures, and provider identity.

### Playwright release gates

1. Run one labelled case across two profiles.
2. Evidence and grades follow canonical result IDs.
3. BM25 and dense score semantics are distinct.
4. Metric and latency deltas render.
5. A controlled hard negative is visible.
6. Elasticsearch index/version identity is visible.
7. Downloaded report fingerprint matches UI.

---

## 26. Performance validation

Measure but do not claim production scale:

- indexing and embedding time;
- p50 and p95 query latency;
- stage latency;
- model-load and inference latency;
- total latency;
- index size;
- memory observations where available.

Warm-up policy must be explicit. Cold and warm Cross-Encoder runs must not be mixed without labels.

---

## 27. Security and data safety

- No private expert data.
- No secrets in repository.
- Docker binds to localhost by default.
- Dataset licences and provenance are documented.
- Synthetic/reference profiles are clearly identified.
- No claim that results represent a real company.
- No real employment or commercial decision may rely on this dataset.

---

## 28. Documentation deliverables

```text
docs/v0.4.0/spec.md
docs/v0.4.0/domain-model.md
docs/v0.4.0/dataset-card.md
docs/v0.4.0/relevance-guidelines.md
docs/v0.4.0/elasticsearch-index-design.md
docs/v0.4.0/benchmark-protocol.md
docs/v0.4.0/failure-taxonomy.md
docs/v0.4.0/architecture-decisions.md
docs/v0.4.0/validation-report.md
docs/v0.4.0/release-notes.md
```

Recommended repository additions:

```text
src/armie_retrieval/
  datasets/
  indexing/elasticsearch/
  indexing/faiss/
  providers/elasticsearch/
  benchmarks/
  relevance/
  reports/

labs/expert_discovery/
  dataset/
  queries/
  judgements/
  configs/
  reports/

docker/elasticsearch/
docs/v0.4.0/
```

No duplicate Planner or Runtime pipeline may be introduced.

---

## 29. Workstreams

### A — Domain and dataset

Freeze schema, implement generator/loader, build dataset, add provenance, validation, manifest, and dataset card.

### B — Relevance contract

Freeze taxonomy and constraints, write guidelines, build queries and graded judgements, validate hard negatives.

### C — Elasticsearch data plane

Add Docker, mapping, analyzers, synonyms, indexing, aliases, health, and manifest.

### D — Providers

Implement Elasticsearch BM25 and dense retrievers, preserve FAISS, extend Registry and trace contracts.

### E — Benchmark engine

Define profiles, execute query sets, compute category metrics, classify failures, and emit reports.

### F — Query Lab

Expose graded relevance, category data, profile comparison, and failure inspection.

### G — Validation and release

Run architecture review, tests, reproducibility checks, browser gates, documentation, clean release, tag, and GitHub release.

---

## 30. Implementation gates

### Gate 0 — Architecture

- no duplicate runtime;
- no plan mutation;
- explicit providers;
- observational evaluation;
- v0.3.0 flows remain functional.

### Gate 1 — Dataset and judgements

- deterministic dataset;
- approximately 10K records;
- approximately 120 valid queries;
- complete guidelines;
- valid references and hard-negative coverage.

### Gate 2 — Elasticsearch indexing

- reproducible Docker startup;
- versioned mapping;
- matching document count;
- correct alias;
- traceable BM25 smoke query.

### Gate 3 — Dense comparison

- compatible embeddings;
- aligned IDs;
- same query set;
- explicit score semantics;
- measured latency.

### Gate 4 — Hybrid and reranking

- visible RRF contributions;
- enforced candidate bounds;
- bounded BGE;
- explicit fallback;
- valid rank movement.

### Gate 5 — Benchmark validity

- primary profiles complete;
- category metrics complete;
- manifest complete;
- stable expected fingerprint;
- failures classified.

### Gate 6 — Workbench

- real relevance differences visible;
- Evidence and trace agree;
- provider/index identity visible;
- Playwright passes.

### Gate 7 — Release

- all tests pass;
- Docker validation passes;
- reports and documentation complete;
- clean working tree;
- limitations disclosed.

---

## 31. Definition of Done

v0.4.0 is complete when the platform can credibly state:

> ARMIE can run a versioned Expert Discovery benchmark over a realistic dataset, execute Elasticsearch BM25, Elasticsearch Dense, FAISS Dense, Hybrid RRF, and BGE Cross-Encoder profiles through the same controlled runtime, and explain their relevance, latency, and failure trade-offs with reproducible evidence.

It must not claim:

- production traffic validation;
- universal retrieval superiority;
- real-company performance;
- complete Knowledge Graph capability;
- GCP production readiness;
- automated self-optimization.

---

## 32. Codex implementation rules

Codex must:

1. Inspect the repository before editing.
2. Read architecture-freeze and release documents.
3. Reuse existing Planner, Runtime, Registry, Trace, Evidence, Verification, API, and Workbench.
4. Implement one gate at a time.
5. Add failing tests before major behaviour changes.
6. Test real payload content, not only schema existence.
7. Preserve repository-local package loading.
8. Keep source path, commit, and version visible in health diagnostics.
9. Never claim a gate passes without running commands.
10. Record commands and outputs in the validation report.
11. Stop on architecture conflicts rather than silently redesigning.
12. Never download large model weights automatically.
13. Never commit secrets, caches, or Elasticsearch data.
14. Keep commits atomic and reviewable.

Recommended commit sequence:

1. `docs: add v0.4.0 engineering specification`
2. `feat: add expert discovery domain and dataset schemas`
3. `feat: add deterministic dataset builder and validation`
4. `feat: add benchmark query and judgement contracts`
5. `test: add dataset and judgement integrity gates`
6. `infra: add local Elasticsearch Docker environment`
7. `feat: add Elasticsearch index mapping and ingestion`
8. `feat: add Elasticsearch BM25 retriever`
9. `feat: add Elasticsearch dense retriever`
10. `feat: extend registry and retrieval traces`
11. `feat: add v0.4.0 retrieval profiles`
12. `feat: add category-level benchmark evaluation`
13. `feat: add failure taxonomy and reports`
14. `feat: extend Query Lab for graded relevance`
15. `test: add integration and browser acceptance`
16. `docs: add findings and architecture decisions`
17. `release: prepare v0.4.0`

---

## 33. Post-v0.4.0 decision framework

Choose the next direction from evidence:

- **Knowledge Graph:** relationship and multi-hop failures are material.
- **ANN performance:** dense latency or memory becomes dominant.
- **GCP deployment:** local relevance architecture is stable.
- **Recommendation systems:** queryless discovery or personalization becomes a real target.
- **Index lifecycle:** freshness, updates, or schema migration becomes the dominant risk.

The release report must make one evidence-backed recommendation.

---

## 34. Release positioning

Long form:

> ARMIE Retrieval Platform v0.4.0 introduces a reproducible Expert Discovery relevance-engineering lab with versioned data, graded judgements, Elasticsearch BM25 and dense retrieval, FAISS comparison, hybrid fusion, Cross-Encoder reranking, failure analysis, and evidence-backed retrieval strategy evaluation.

Concise:

> A local-first Retrieval Control and Evaluation Plane for measurable Expert Discovery search quality.
