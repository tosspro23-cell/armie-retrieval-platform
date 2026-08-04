# Gate 5 Dataset Card

## Dataset

- Synthetic Expert Discovery dataset: 10,000 profiles.
- Source checksum: `9f595cb7c84f6fc2b2a2a691526f86ccdb6f96e4675f8ce002ac0e5466689291`.
- Runtime index: `armie-experts-v1-gate23b-20260803` in Elasticsearch 8.15.3.
- Query set: 120 deterministic queries across ten categories.
- Gold: 35 queries, stratified as 4 exact-skill, 4 skill+industry, 4
  delivery/project, 3 organization, 3 seniority/role, 4 multi-constraint, 4
  semantic-paraphrase, 3 hard-negative, 3 temporal, 3 negative-constraint.
- Silver: remaining 85 queries.

## Audit findings

The generated corpus has 9,496 duplicate normalized summaries out of 10,000
profiles and repeated templated language. This is a material benchmark risk:
scores should not be generalized to natural expert-network data. Query terms
and generated structured fields share a controlled vocabulary, so label leakage
risk is high. Gold is an independent structured audit, not external human
ground truth.

The benchmark includes employer/client ambiguity, delivery-versus-mention
ambiguity, temporal constraints, negative constraints and hard-negative cases.
All Gold judgements record evidence references, rationale codes and correction
history; Silver labels retain `silver_rule_assisted` status.

The full audit and per-query evidence are emitted by
`examples/run_v040_gate5.py` as a machine-readable benchmark artifact. They
are intentionally not committed as generated data or reports.
