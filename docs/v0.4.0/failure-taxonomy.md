# Failure Taxonomy

The benchmark layer uses explicit codes for missing evidence, schema gaps,
lexical mismatch, semantic false positives, filter and constraint failures,
employer/client ambiguity, delivery-mention ambiguity, fusion displacement,
reranker regression, candidate-pool misses, stale experience, near duplicates,
judgement gaps, planner routing errors, backend inconsistency, and
graph-relationship needs.

Gate 5 reports failures per query with profile, expected grade-3 IDs, returned
IDs, evidence, stage and code. A retrieval failure is kept distinct from a
judgement gap: a low score caused by an ambiguous or synthetic label is not
reported as an algorithm defect without supporting evidence.
