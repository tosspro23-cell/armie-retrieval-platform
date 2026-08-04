# Relevance Guidelines

Grades are 3 (all required constraints independently verified), 2 (relevant
but not fully verified), 1 (partial evidence), and 0 (not relevant or a
prohibited constraint violation). Reviewers distinguish project delivery from
a summary mention, and employment at an organization from delivery for that
organization.

Gate 5 has two explicit tiers:

- **Gold (35 queries):** stratified across all ten categories. Each profile is
  independently checked against structured fields and source evidence outside
  the tested ranking. Judgements record evidence references, rationale codes,
  reviewer `codex-independent-structured-audit`, status `gold_reviewed`, and
  correction history relative to the rule-assisted draft.
- **Silver (85 queries):** the remaining generated queries and their original
  rule-assisted labels. These are marked `silver_rule_assisted` and are lower
  confidence; they must not be presented as human ground truth.

The dataset is synthetic and highly templated. Gold therefore means an
independent structured audit of this dataset, not external human annotation.
The audit explicitly records leakage, duplicate-summary and ambiguity risks.
