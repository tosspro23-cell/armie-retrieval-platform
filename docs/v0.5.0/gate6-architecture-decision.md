# Gate 6 — Architecture Decision

**Decision:** D — evidence invalid/inconclusive; protocol-preserving
re-execution required

The frozen arms were executed against the locked corpus and index, but the
benchmark extension has two contract defects: retrieval query text and
relevance judgement source are not the same semantic query, and negative
requirements were serialized as hard `not_in` constraints rather than the
separate exclusion collection. Relevance was anchored to base v2 query IDs
while the executed text was constraint-only. The exclusion encoding also
prevents an independently interpretable prohibited-violation metric. Together
these violate the intended relevance/eligibility separation boundary.

The raw result package remains preserved for audit. It must not be used to
promote C1, retain C2, or claim a valid C0 comparison. The corrective action is
to create a new versioned extension fingerprint whose semantic query text is
the base semantic query plus the frozen structured constraints, serialize
exclusions in the separate contract field, regenerate the corresponding Gold
audit without changing Dataset v2 or runtime semantics, and rerun the same five
arms only after a new protocol review.

Observed but non-decisive findings:

- C1 removed known hard violations in this run.
- C1 exceeded the 5 percentage-point NDCG guardrail.
- C2 did not improve aggregate eligible recall/fill over C1.
- C2 E2E latency increased with candidate pool size.
- C3 remains deferred; no complementary C1/C2 evidence was established.

No source runtime, Dataset v2, v0.4 benchmark, Workbench, tag or remote state
was changed by the benchmark execution.
