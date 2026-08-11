# Dataset Card — `expert-discovery-v2-realism`

## Gate 5.5A refinement (r2)

The r2 pilot is a bounded human-review refinement of the original pilot. It
improves role/seniority diversity, structural narrative variation,
query-category semantics, structured grade rules, low-overlap indirect cases
and hard-negative quality. It preserves the independent document/query/
judgement pipelines and immutable Dataset v1. This remains a **controlled
synthetic relevance benchmark**, not external human ground truth or validated
real-world expert-search quality.

## Summary

Dataset v2 is a controlled synthetic relevance benchmark pilot for validating
retrieval infrastructure and relevance measurement. The default pilot contains
750 profiles, 40 queries spanning all ten query categories, and draft
canonical-truth judgements. The Gate 5.5B full corpus contains 10,000 profiles,
120 queries, and 1,200,000 judgements. Neither is a production dataset.

## Data generation

Profiles are generated from canonical concepts and typed relationships, then
projected into varied document language. Queries are generated independently
with a separate seed and query-only surface lexicon. Judgements are generated
from canonical concepts, relationship edges, temporal records and evidence
references; they never inspect generated text or retrieval output.

## Schema and provenance

The manifest pins schema, generator, projection, ontology, surface lexicon,
relationship, temporal, evidence, query and judgement versions. Evidence records
identify source profile, evidence kind and structured object references. Gold
records are marked `draft_gold_structured_audit`; Silver records are explicitly
`draft_silver_rule_assisted`.

## Known limitations

- The v1 corpus has 9,496 duplicate normalized summaries out of 10,000.
- Synthetic language remains partly templated and uses a controlled vocabulary.
- Controlled-vocabulary leakage can inflate retrieval metrics.
- Gold is an independent structured audit, not external human ground truth.
- Results must not be generalized to natural expert-network data.

The appropriate description is **controlled synthetic relevance benchmark**.

Gate 5.5B executed the frozen H1–H4 runtime on 103 Gold queries and 17 Silver
monitoring queries. Gold and Silver are isolated by judgement contract; Silver
is rule-assisted and must not be presented as Gold truth. Metrics and stability
classifications are documented in `gate55b-results.md` and
`benchmark-stability-report.md`.
