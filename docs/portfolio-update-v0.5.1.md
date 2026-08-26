# ARMIE Retrieval Platform — Portfolio Update

**Current public baseline:** v0.5.1 released / closed  
**Repository:** https://github.com/tosspro23-cell/armie-retrieval-platform  
**Release:** https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1  
**Purpose of this document:** public-facing portfolio source material for explaining the project’s engineering value, architecture, evidence, and current maturity without overstating what has been validated.

---

## 1. Project in one sentence

ARMIE Retrieval Platform is a production-oriented retrieval systems laboratory that separates planning, retrieval execution, constraints, result processing, observability, evaluation, and product UX into explicit contracts — then validates those contracts through reproducible datasets, real Elasticsearch execution, browser-level tests, and governed release gates.

The current released product line focuses on **Expert Discovery**, but the core runtime was intentionally designed around domain-neutral retrieval contracts rather than a single hard-coded object type.

---

## 2. What is new in v0.5.1

v0.5.1 adds a governed natural-language layer on top of the deterministic C1 constraint-aware retrieval substrate released in v0.5.0.

The released execution path is:

```text
Natural-language request
→ bounded interpretation
→ clarification when intent is ambiguous or unsafe
→ explicit user resolution
→ final confirmation
→ canonical RetrievalContract
→ deterministic validation / compilation
→ existing C1 Elasticsearch retrieval
→ results + provenance
```

The key design choice is that natural-language interpretation is **not** allowed to silently become executable hard constraints.

If intent is ambiguous, the system asks for clarification. If the interpretation changes after confirmation, the previous execution authorization is invalidated. Unsupported meaning cannot fabricate a constraint the runtime does not actually support.

This release therefore does **not** claim unrestricted natural-language understanding. It demonstrates a safer engineering pattern for combining probabilistic language interfaces with deterministic retrieval execution.

---

## 3. Why this project matters technically

### 3.1 It treats retrieval as a system, not a single vector-search call

The platform separates:

- `Query`
- `RetrievalPlan`
- `RetrievalRuntime`
- retrievers and provider registries
- result processors
- `RetrievalResult` / `ResultItem`
- trace and provenance
- evaluation
- offline index construction
- product/application orchestration

This makes retrieval strategies replaceable and testable without collapsing planning, infrastructure, ranking, filtering, and evaluation into one opaque function.

The architecture supports Dense, Sparse/Keyword, Hybrid/RRF, graph retrieval, reranking, offline index builders, and multiple provider implementations while retaining one shared runtime contract.

### 3.2 It separates probabilistic interpretation from deterministic authority

The most important v0.5.1 architecture boundary is:

```text
probabilistic / ambiguous language
        ↓
Candidate interpretation
        ↓
clarification + user confirmation
        ↓
deterministic RetrievalContract
        ↓
validator / compiler
        ↓
retrieval execution
```

This prevents a model or heuristic from gaining execution authority simply because it produced a plausible interpretation.

The system explicitly distinguishes concepts such as:

- required constraints
- exclusions
- preferences
- context-only information
- unsupported meaning
- ambiguous meaning

Only confirmed, supported intent can reach the deterministic C1 execution boundary.

### 3.3 It uses failure evidence to shape architecture

A major part of the v0.5.1 work was not feature accumulation; it was learning where automation was unsafe.

Rule-based semantic role classification looked strong on small development fixtures, then collapsed on a valid prospective held-out benchmark. A larger local model also failed to provide safe semantic-role judgment: some roles improved, but false hardening remained unacceptable.

Instead of tuning indefinitely against the benchmark, the architecture changed direction:

```text
uncertain semantic role
→ clarification
→ user resolution
```

That decision is a core engineering result of the project: evaluation changed the product architecture rather than being used only to decorate a completed implementation.

---

## 4. Production-style retrieval evidence

### Dataset / benchmark identity

The current controlled synthetic Expert Discovery Dataset v2 contains:

- **10,000 expert profiles**
- **120 benchmark queries**
- version: `v2-realism-full`
- checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`

This dataset is explicitly treated as a controlled synthetic benchmark, not as proof of real-world expert-search quality.

### Elasticsearch execution

The released C1 path has been validated against:

- Elasticsearch **8.15.3**
- logical alias: `armie-experts-v0.5-dense`
- physical index: `armie-experts-v1-v2-gate6b-dense-10000`
- **10,000 documents**
- embedding model: `BAAI/bge-m3`
- embedding dimensions: **1024**
- native pre-filtered dense retrieval
- strict shortfall / no-backfill semantics

Representative real-runtime scenarios covered numeric constraints, seniority, conjunctions, exclusions, high-selectivity zero-result behavior, unsupported intent rejection, confirmation enforcement, and the semantic-only path when no hard constraints remain.

### Browser-level validation

The final Founder-critical live Playwright verification passed:

- **16 passed**
- **0 failed**
- **0 skipped**

The browser suite exercises the real Workbench + backend + Elasticsearch path, including:

- unresolved clarification cannot execute
- resolved but unconfirmed interpretation cannot execute
- editing a confirmed interpretation invalidates prior execution authority
- new sessions do not reuse stale state
- positive-result and legitimate zero-result states are distinct
- backend result counts match visible result cards
- manual structured C1 remains functional

---

## 5. Engineering capability demonstrated

This project is useful as a portfolio piece because the strongest evidence is not a single algorithm. It demonstrates end-to-end systems engineering across several layers.

### Architecture and boundaries

- Designed a shared retrieval runtime around declarative plans and replaceable providers.
- Preserved a deterministic execution substrate while adding a natural-language product layer.
- Kept planner, runtime, evaluation, observability, and offline learning concerns separate.
- Established explicit ownership boundaries between interpretation, contract validation, retrieval execution, and UI state.

### Retrieval engineering

- Dense retrieval with BGE-M3 embeddings.
- Sparse / keyword retrieval.
- Hybrid retrieval with Reciprocal Rank Fusion.
- Graph retrieval experiments.
- Cross-encoder reranking experiments.
- Native Elasticsearch metadata pre-filtering for hard constraints.
- Strict no-relaxation / no-backfill semantics for constrained retrieval.

### Evaluation-driven development

- Built versioned datasets, query sets, judgments, manifests, and fingerprints.
- Compared multiple retrieval hypotheses rather than promoting components by intuition.
- Used prospective held-out benchmarks to detect development-set overfitting.
- Rejected model/rule candidates when they failed safety or generalization thresholds.
- Distinguished experimental evidence, diagnostic evidence, and promotion evidence.

### AI safety at the application boundary

- Identified **false hard constraints** as the highest-risk interpretation failure because they can irreversibly remove valid candidates before ranking.
- Added clarification rather than allowing uncertain meaning to silently become executable.
- Required explicit confirmation before natural-language-derived hard constraints execute.
- Prevented unsupported meaning from becoming fabricated DSL/runtime behavior.
- Invalidated stale confirmation when interpretations are edited.

### Full-stack product integration

- Typed FastAPI application surface.
- React/Vite Workbench.
- Structured clarification and confirmation UX.
- Canonical result rendering shared by manual and confirmed-NL execution.
- Explicit not-executed, executed-zero, and executed-with-results states.
- Live Playwright verification against the real backend and Elasticsearch runtime.

### Reproducibility and release engineering

- Versioned release artifacts and immutable release tags.
- Runtime/index compatibility checks.
- Dataset and projection fingerprints.
- GitHub Release publication for v0.5.1.
- Repository governance with explicit work objects, bounded gates, result packages, acceptance boundaries, and post-push reconciliation.
- Current CI baseline passes on Python **3.9 and 3.11** after a dedicated CI-revival pass; the current local regression baseline records **196 tests with zero failures** plus the dedicated pytest dense-index tests.

---

## 6. A key engineering story: refusing the wrong automation

One of the most portfolio-relevant parts of the project is the decision process around natural-language constraint interpretation.

The initial hypothesis was that semantic role judgment could be automated directly with deterministic rules or a local model.

Prospective evaluation showed otherwise:

- a deterministic staged candidate that looked strong on development evidence dropped sharply on the valid held-out benchmark;
- qwen3:8b could produce structured role output when span extraction was removed from its task, but role accuracy remained insufficient and false `REQUIRED` classifications were unsafe;
- stronger automation was therefore **not promoted** simply because an LLM was available.

The product architecture moved to:

```text
high-confidence supported intent
→ candidate interpretation

unsafe / ambiguous intent
→ clarification required
→ user resolves intent
→ confirmation
→ deterministic execution
```

This demonstrates a practical principle that applies far beyond retrieval:

> Use models where they add measured value; keep deterministic contracts around authority-sensitive execution; route unresolved uncertainty back to the user instead of hiding it.

---

## 7. Current architecture maturity beyond Expert Discovery

A recent read-only second-domain readiness review evaluated whether the current platform core could support **Companion Memory** as another retrieval domain without turning Memory into an `ExpertProfile` or moving runtime truth authority into the retrieval engine.

The review found that the core substrate is substantially more domain-neutral than the current Expert Discovery product composition.

Reusable generic components include:

- `Query`
- `RetrievalPlan`
- `ResultItem`
- `RetrievalResult`
- `RetrievalRuntime`
- provider/retriever/processor registries
- generic in-memory retrieval
- generic FAISS index building and retrieval
- generic keyword index building and retrieval
- shared evaluation metrics

The architecture freeze explicitly allows a `ResultItem` to represent an expert, document, **memory**, incident, company, or other knowledge object.

The same review also identified the parts that should **not** be generalized prematurely:

- ExpertProfile dataset contracts
- current Expert Elasticsearch mapping/index builder
- Expert C1 constraint registry and compiler
- Expert planner defaults
- Expert graph projection
- Expert-oriented rerank document serialization
- Workbench-specific API composition

The resulting readiness classification was:

> **READY_FOR_B2_WITHOUT_PLATFORM_CHANGE**

for a bounded second-domain proof using the generic library/runtime path and dedicated Memory artifacts.

This is an architecture-readiness finding, **not** a claim that the live Companion Memory B2 integration has already shipped.

---

## 8. What I would highlight on a portfolio website

### Recommended project headline

**ARMIE Retrieval Platform — Evaluation-driven retrieval systems engineering with governed natural-language constraints**

### Recommended one-line description

A production-oriented retrieval platform that combines dense/sparse/hybrid retrieval, deterministic constraint execution, observability, evaluation, and a governed natural-language clarification workflow — validated end-to-end against Elasticsearch and live browser tests.

### Recommended proof points

- **10K** controlled synthetic expert profiles
- **120** versioned evaluation queries
- **16/16** live Founder-critical Playwright scenarios passing
- Elasticsearch **8.15.3** real-runtime C1 validation
- BGE-M3 **1024-d** dense embeddings
- Native deterministic hard-constraint pre-filtering
- Explicit clarification + confirmation safety boundary
- Manual structured and governed-NL paths converge on one canonical `RetrievalContract`
- Current CI green on Python **3.9 / 3.11**
- Released and published as **v0.5.1**

### Recommended engineering themes

1. **System architecture over API glue** — planning, retrieval, processing, evaluation, and observability are explicit layers.
2. **Evaluation changes architecture** — failed generalization led to clarification rather than endless benchmark tuning.
3. **Probabilistic UX, deterministic execution** — language understanding does not directly own retrieval authority.
4. **Evidence before promotion** — rules, models, rerankers, and strategies are promoted only when measured evidence supports them.
5. **Full-stack validation** — browser → API → contract → Elasticsearch → result rendering is exercised as one live system.
6. **Reproducibility** — datasets, index identities, fingerprints, manifests, release tags, and governance state are explicit.
7. **Platform thinking** — the core runtime can support a second domain without forcing that domain into Expert Discovery semantics.

---

## 9. Suggested architecture visual for the website

A compact diagram should show two layers.

### Product path

```text
Natural-language query
        ↓
Interpretation
        ↓
Clarification if needed
        ↓
User confirmation
        ↓
RetrievalContract
        ↓
C1 deterministic compiler
        ↓
Elasticsearch Dense + hard pre-filter
        ↓
Ranked results + provenance
```

### Platform substrate

```text
Query
  ↓
RetrievalPlan
  ↓
RetrievalRuntime
  ├─ Dense
  ├─ Sparse / Keyword
  ├─ Hybrid / RRF
  └─ Graph
  ↓
Result processors / reranking
  ↓
RetrievalResult
  ├─ provenance / trace
  └─ evaluation
```

The visual should make it clear that the v0.5.1 governed language layer sits **above** the existing retrieval substrate rather than replacing it.

---

## 10. Public claims to avoid

For an accurate portfolio presentation, do **not** claim that the project has already proven:

- production quality on real expert-network data;
- unrestricted natural-language understanding;
- autonomous safe hard-constraint extraction for arbitrary queries;
- live Companion Memory B2 integration;
- production multi-tenant deployment;
- universal cross-domain constraint semantics.

The strongest story is more credible:

> A retrieval platform was built, measured, stress-tested, and deliberately constrained where evidence showed automation was unsafe.

---

## 11. Public references

- Repository: https://github.com/tosspro23-cell/armie-retrieval-platform
- v0.5.1 Release: https://github.com/tosspro23-cell/armie-retrieval-platform/releases/tag/v0.5.1
- v0.5.1 Release notes: `docs/v0.5.1/release-notes.md`
- Gate 5 confirmed interpretation → C1 evidence: `docs/v0.5.1/gate5-confirmed-c1-e2e.md`
- Architecture Freeze: `docs/architecture-freeze-v1.md`
- Repository overview: `docs/repository-overview.md`

---

## 12. Portfolio positioning

The project should be positioned primarily as evidence of **AI systems engineering judgment** rather than as a claim that one retrieval algorithm beats every alternative.

The strongest proof is the combination of:

- architecture discipline;
- retrieval and ranking implementation;
- deterministic contracts around high-risk AI behavior;
- controlled model experiments;
- prospective evaluation;
- full-stack integration;
- browser-level live validation;
- reproducible release engineering;
- explicit refusal to promote components that did not meet evidence thresholds.

That combination demonstrates the ability to take an AI capability from research hypothesis through architecture, implementation, evaluation, product UX, runtime integration, regression testing, and public release — while preserving clear boundaries about what the evidence does and does not prove.
