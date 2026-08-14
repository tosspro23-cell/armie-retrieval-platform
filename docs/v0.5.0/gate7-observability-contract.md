# Gate 7 Observability Contract

Every C1 result exposes a stable, presentation-independent provenance record.

## Required fields

- `strategy_identity`: `C0` or `C1`;
- `runtime_source`: dense Elasticsearch or native pre-filter;
- contract id and version;
- validation state and typed error category;
- semantic constraint trace: canonical field, projection field, operator,
  normalized value, polarity, scope, executability, reason, and whether a DSL
  clause was applied;
- supported/unsupported counts and capability-registry snapshot;
- requested, returned, and strict-shortfall counts;
- index compatibility result and configured index identity;
- stage timings for validation, filter compilation, dense execution, and total
  retrieval latency.

`RetrievalPlan` remains declarative. Providers execute it but never mutate the
plan. Unsupported contracts do not trigger backend calls or implicit fallback.
Provider scores remain provider-specific and are not compared as if they were
common metrics.

## Typed outcomes

`VALID` means the C1 contract was executable. `NON_EXECUTABLE` with
`UNSUPPORTED_CONSTRAINT` identifies a deferred or unsupported contract.
`INDEX_INCOMPATIBLE` identifies a failed projection/index compatibility gate;
`NO_RESULTS` identifies an empty compatible execution. Shortfall is represented
as a successful result with a non-zero shortfall count and category
`STRICT_SHORTFALL`; the reason is deliberately bounded to
`eligible_universe_or_retrieval_shortfall` and does not claim corpus-wide
scarcity.
