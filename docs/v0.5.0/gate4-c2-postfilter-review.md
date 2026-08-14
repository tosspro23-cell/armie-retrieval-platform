# Gate 4 — C2 controlled post-filter review

**Status:** Gate 4 engineering smoke experiment complete; not formal C0–C3
benchmark evidence. Gate 5 and C3 are not started.

## Runtime architecture

```text
C0: H2 Dense
C1: H2 Dense + native Elasticsearch pre-filter
C2: H2 Dense candidate pool N + deterministic post-filter
```

C2 wraps the existing Dense retriever, requests one explicit candidate-pool
size (`10`, `20`, `30`, `50`, or `100`), verifies structured metadata, and
keeps original Dense score/order among eligible items. It never reranks or
automatically expands N.

## Verification semantics

Required constraints use `SATISFIED`, `VIOLATED`, `UNKNOWN`; both VIOLATED and
UNKNOWN are excluded under strict policy. Exclusions use the inverse polarity.
Verification reads canonical projection fields only, never summaries, query
text, embeddings or LLM judgements. Per-candidate audit records retain IDs,
operator, expected/observed values, status and projection field.

Supported scope is the same bounded C1 profile scope: industry, role, location,
years_experience and seniority. Temporal, employer/client, relationship,
delivery/advisory and prohibited-capability semantics remain deferred.

## Targeted smoke observations (Top-K = 5)

| Case | Strategy/N | Eligible returned | Shortfall | Observation |
|---|---|---:|---:|---|
| years >= 20 | C0 | control | n/a | may include ineligible candidates |
| years >= 20 | C1 | all returned eligible | 0.. | native pre-filter control |
| years >= 20 | C2/10 | 2 in fixture | 3 | no backfill; Dense order preserved |
| years >= 20 | C2/20,30,50,100 | explicit N, no expansion | data-dependent | each N is a separate run |
| Energy + years >=20 + seniority >= senior | C1/C2 | conjunction only | visible | bool AND semantics |
| Engineer + exclude Banking | C1/C2 | Banking removed | visible | `must_not` polarity preserved |

The deterministic fixture returned B then D for a years>=20 C2/10 run, despite
only two eligible candidates, proving strict shortfall and Dense-order
preservation. C2 candidate pool parameter is present in provenance for every
run. No aggregate winner or saturation claim is made from this small fixture;
formal Gate 6 is required for that.

## Latency and diagnostics

C2 provenance records candidate pool size, retrieved/eligible counts, status
counts, shortfall, verification latency and end-to-end latency. Dense latency
is retained from the underlying H2 provider. Tiny smoke timings are raw
engineering observations, not p50/p95 claims.

## C1/C2 and continuation assessment

C1 and C2 enforce the same approved profile semantics through different
mechanisms. C2 is useful as a controlled verification/research path and for
candidate-pool sensitivity experiments; whether it is retained for Gate 6
requires the formal C0–C3 benchmark. C3 is not warranted by this bounded
smoke alone and remains unauthorised.

## Limitations and skipped tests

No formal H1–H4 or C0–C3 benchmark, Workbench, frontend or Playwright tests
were run. The full suite's existing skips are environment-gated v0.4
Elasticsearch integration tests (`test_real_elasticsearch_health` and
`test_real_index_search`); they do not invalidate the Gate 4 deterministic
post-filter tests. A separate isolated Elasticsearch proof for C1 was already
completed in Gate 3; C2 verification itself uses backend-neutral structured
fixtures in this bounded gate.
