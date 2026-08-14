# Gate 2 projection and compiler review

**Status:** Gate 2A evidence package and bounded Gate 2B/2C compiler complete;
Gate 3 and runtime integration remain out of scope.

## Evidence and identities

- Dataset: `v2-realism-full`, 10,000 profiles, checksum
  `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`.
- Projection schema: `armie-v0.5-constraint-projection-v1`.
- Projection implementation: `constraint-projection-0.1`.
- Mapping fingerprint is emitted by `projection_manifest()` and changes with
  the canonical mapping.
- The released v0.4 index is not modified.

## Field × operator × scope approval

| Scope/field | Operators | Gate 2 approval | Reason |
|---|---|---|---|
| profile `industry` | EQ, NEQ, IN, NOT_IN | YES | complete canonical profile field and keyword projection |
| profile `role` | EQ, NEQ, IN, NOT_IN | YES | complete canonical profile field and keyword projection |
| profile `location` | EQ, IN, NOT_IN | YES | complete canonical profile field; no text fallback |
| profile `years_experience` | GTE, GT, LTE, LT, BETWEEN | YES | integer source contract and versioned integer projection |
| profile `seniority` | EQ, IN, NOT_IN, GTE, GT, LTE, LT | YES | explicit rank 1/2/3; never lexical ordering |
| nested employer | EQ/IN organization | DEFERRED | nested mapping is designed but isolated ES filter evidence remains pending |
| nested project client | EQ/IN client | DEFERRED | nested mapping is designed but isolated ES filter evidence remains pending |
| temporal intervals | AFTER, BEFORE, BETWEEN | NO | overlap semantics intentionally not frozen |
| relationship predicate/object/time | EQ/IN | NO | nested integrity requires isolated ES validation and contract scope decision |
| delivery/advisory evidence | EQ/IN | NO | evidence-aware semantics remain deferred |
| prohibited capability | exclusions | NO | no authoritative negative projection |

`YES` means only the listed profile-level semantics may be compiled. Nested
and temporal rows must return explicit non-executable results, not text-search
fallbacks or arbitrary DSL.

## Intermediate planning boundary

```text
RetrievalContract → validated ConstraintPlan → allow-listed ES compiler → DSL
```

`ConstraintPlan` retains executable status, canonical constraint ID, DSL (when
approved), and a reason when non-executable. The compiler owns a fixed
canonical-field allow-list and fixed operator mapping; user field names,
scripts, arbitrary DSL and unknown operators are rejected.

The semantic plan itself is backend-neutral: it carries canonical field,
projection field, scope, operation, normalized value, polarity (`REQUIRED` or
`EXCLUDED`), executability and a non-executable reason. Elasticsearch DSL is
added only by the translation step, so C1/C2/C3 can reuse the same boundary.

Seniority equality uses the canonical enum field (`mid`, `senior`,
`principal`); ordered operations use `seniority_rank` with explicit values
`1/2/3`. Unknown enum values are non-executable. Exclusions are always
translated as negative polarity (`must_not`) without requiring callers to
invert operators.

## Temporal decision

Temporal compilation is deferred. Gate 2 does not silently choose overlap,
containment, or start-within semantics. The source distinguishes closed
project intervals, open-ended current employment, and unspecified relationship
intervals; a future gate must choose explicit operation semantics and test them.

## Mapping and isolation status

The versioned mapping uses integer, keyword, date and nested types and preserves
employer/client/relationship correlation. An isolated temporary index was
validated against Elasticsearch 8.15.3:

- `years_experience >= 20` returned exactly `D, E`; unknown experience did not match.
- `seniority >= senior` returned `B, C, D, E`; the emitted value was numeric rank `2`.
- same-employment Shell + Director fixture returned no match across separate
  employment records.
- employer `worked_at Shell` matched the employment record only; a Shell
  project client did not satisfy it.

The temporary index was deleted after validation. No v0.4 index, alias, H1–H4,
C0–C3 or runtime filtering was changed or run.

## Non-executable behavior and blockers

Unsupported contracts, unsupported fields/operators, invalid contracts and
deferred nested/temporal semantics remain explicit non-executable outcomes.
Before Gate 3, run isolated Elasticsearch mapping/filter fixtures and approve
or reject nested employer/client operations. Do not integrate this compiler
into H2 or C1 runtime paths yet.
