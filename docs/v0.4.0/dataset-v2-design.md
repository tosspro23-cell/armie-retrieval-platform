# Dataset v2 Realism Design

**Identity:** `expert-discovery-v2-realism`  
**Stage:** Gate 5.5A refinement pilot (r2)  
**Positioning:** controlled synthetic relevance benchmark

Dataset v2 is a bounded pilot (500–1,000 profiles; default 750 profiles and 40
queries). It is not a production corpus and it must not be presented as
validated real-world expert-search quality.

The r2 refinement was triggered by qualitative human review despite machine
integrity gates passing. It preserves the approved independent pipelines while
improving role diversity, structural narrative diversity, query-taxonomy
semantics, structured grade rules, low-overlap indirect cases and hard
negative construction.

## Immutable v1 boundary

`expert-discovery-v1-controlled` remains unchanged. The v1 generator, schema,
projection and checksum are regression-tested. v2 is written to its own
`knowledge/`, `queries/` and `judgements/` directories and never overwrites v1
artifacts.

## Versioned identity

The v2 manifest records schema, generator, projection, ontology, surface
lexicon, relationship, temporal, evidence, query and judgement versions. The
manifest checksum covers canonical profile truth and the pilot has independent
document and query seeds.

## Three independent pipelines

```text
Canonical structured truth + ontology IDs
        ├── Document/profile generator (document surface lexicon)
        ├── Query generator (query surface lexicon, independent seed)
        └── Judgement builder (canonical truth, relationships, dates, evidence)
```

The judgement builder cannot read `search_document`, `query_text` or retrieval
results. The document and query generators do not share textual templates,
surface phrases, direct query-to-document mappings or random seeds. They share
only canonical ontology identifiers and structured truth.

## Representation and relationships

Each profile carries canonical concepts, document surface fields, explicit
employment and project records, temporal intervals, typed relationship edges
and evidence provenance. Employer, client, partner, vendor and advisory edges
are distinct. Project delivery, advisory exposure, certification, skill mention
and explicit-span evidence are separately typed.

The three-layer representation is explicit:

1. canonical concept / ontology ID;
2. document/profile surface language;
3. query surface language.

Temporal validation rejects reversed intervals and checks that project delivery
falls within plausible employment/advisory spans. Current and historical roles
are represented separately.

## Refinement controls

Roles are selected from a controlled catalogue and paired with compatible
seniority and experience bands. Summaries use nine distinct narrative families
with opening-pattern diagnostics. Queries carry explicit relationship, evidence,
role, seniority, industry, temporal and prohibited-constraint fields; category
labels are audited against those fields. Grades are derived from structured
truth: a complete canonical and evidence match is Grade 3, incomplete but useful
matches are Grade 2, partial or adjacent evidence is Grade 1, and missing or
contradicted requirements are Grade 0. `hard_negative` is never itself a reason
to assign Grade 1.

The r2 pilot includes a controlled low-overlap indirect semantic bucket and
typed near-miss hard negatives (relationship, advisory-only, time-window and
missing-skill cases).

Multi-constraint language is contract-checked: an industry phrase is required
in `industry_required`, and “technical leadership required” is represented in
both `required_capabilities` and `canonical_required`, never as an optional
constraint. Query validation fails closed on any mismatch. Negative metrics
distinguish ordinary Grade-0 rows from true structured near-misses; the legacy
hard-negative density is retained only as a labelled compatibility value.

## Quality gates

The pilot audit records count, checksum, exact and near duplicates, n-gram ratio,
lexical diversity, style/template frequency, length distribution, query/document
surface overlap, relationship and temporal coverage, evidence provenance, hard
negative density, grade/category distributions, leakage risks and invalid
records. A deterministic manual-inspection sample contains at least 20 profiles
and 20 queries, including grade 3/2/1/0 cases where available.

The surface-overlap diagnostic uses shared three-token phrases rather than
generic words, making templated leakage visible and comparable with v1.

## Limitations

The v1 reference corpus contains **9,496 duplicate normalized summaries out of
10,000**, templated synthetic language and controlled-vocabulary leakage risk.
Gold is an independent structured audit, not external human ground truth.
Neither v1 nor this v2 pilot should be generalized to natural expert-network
data.
