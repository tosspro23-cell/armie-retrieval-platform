# Gate 7 — C1 Runtime Productization

Status: implementation candidate, pending Gate 7 review. No release, tag, or
push is implied by this document.

Gate 6D selected **Decision A**: promote C1 native pre-filtering for the
supported profile-level constraint subset; de-prioritize C2 and keep C3
deferred. Gate 7 turns that decision into a bounded runtime contract without
changing planner, retriever, registry, or dataset architecture.

## Runtime contract

- No contract selects the unchanged C0 dense path.
- A valid supported `RetrievalContract` selects C1 and applies an allow-listed
  Elasticsearch `knn.filter`.
- Unsupported, deferred, invalid, or ambiguous constraints return an explicit
  non-executable result and do not call Elasticsearch. There is no silent
  relaxation and no C2 fallback.
- A real Elasticsearch C1 request must prove compatibility with the v0.5
  projection schema and 1024-dimensional BGE-M3 vector field before execution.
  Incompatibility is an observable `INDEX_INCOMPATIBLE` outcome.
- Strict shortfall is a successful constrained execution with explicit
  requested, returned, and shortfall counts; it is not a runtime failure.

## Supported registry

The authoritative registry is exposed at `/api/v1/constraints/registry` and
contains only profile-level `industry`, `role`, `location`,
`years_experience`, and `seniority` capabilities with their approved
operators. Temporal, relationship, delivery, and evidence constraints remain
deferred and are never inferred from free text.

## Frozen identities

The runtime records the Gate 6B projection schema
`armie-v0.5-constraint-projection-v1`, BGE-M3/1024 dimensions, the configured
C1 index, and the capability-registry version in provenance. The default C1
index is configurable through `ARMIE_V050_C1_INDEX`; deployment configuration
must point it at the verified Gate 6B-compatible index or alias.

The expected Gate 6B projection implementation is
`constraint-projection-0.2-gate6b`, with mapping fingerprint
`e7f3acf23f2d90964e4e771da14bb033b93d386a6e73c4d351a91a40cfba5a0d`, dataset
lineage `v2-realism-full`, and checksum
`514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`.

This remains a controlled synthetic validation path. Gate 6D benchmark results
are evidence for the promotion decision, not a claim of production or
real-world expert-search quality.
