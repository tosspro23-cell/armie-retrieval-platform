# Gate 6B — Projection Repair Review

**Status:** Projection parity passed; controlled re-evaluation complete.

Gate 6B preserved the v1.1 benchmark and changed only the deterministic
projection/index identity. Gate 6M, Gate 6A, Dataset v2, and the historical
index remain preserved.

## Root cause and repair

Gate 6A reproduced that the historical dense mapping omitted
`years_experience` and `seniority_rank`, even though Dataset v2 canonical
profiles contain `years_experience` and `seniority`. Gate 6B now projects:

`Dataset v2 canonical truth → constraint-projection-0.2-gate6b → isolated ES index`

The projection adds the approved fields only; it does not add temporal,
relationship, delivery, or advisory runtime semantics.

## Identity

- Dataset: `v2-realism-full`, 10,000 profiles
- Dataset checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
- Benchmark: `v0.5-constraint-extension-v1.1`
- Fingerprint: `6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb`
- Index: `armie-experts-v1-v2-gate6b-dense-10000`
- Projection implementation: `constraint-projection-0.2-gate6b`
- Mapping fingerprint: `e7f3acf23f2d90964e4e771da14bb033b93d386a6e73c4d351a91a40cfba5a0d`
- Embedding: `BAAI/bge-m3`, 1024 dimensions
- Elasticsearch: 8.15.3 green, 10,000 documents

## Exhaustive parity

All six supported fields matched canonical truth across all 10,000 profiles:

| Field | Mismatches |
|---|---:|
| years_experience | 0 |
| seniority | 0 |
| seniority_rank | 0 |
| industries | 0 |
| roles | 0 |
| locations | 0 |

Ten native-filter truth probes (numeric, seniority, categorical, exclusion,
two-field, and three-field conjunctions) produced zero false exclusions and
zero false inclusions. The BETWEEN probe is empty in this synthetic corpus,
but its native DSL and parity result are still recorded.

All 85 Gate 6A relevant-and-eligible diagnostic candidates now pass their
repaired native predicates; projection-related false exclusions after repair:
**0**.

## Frozen execution

The same five arms ran across all 46 Gold queries: **230/230**. ANN settings
were unchanged: `k=10`, `size=10`, `num_candidates=20`.

## Validation

- Projection, compiler, C1, C2, Gate 5C, and Gate 6M targeted tests passed.
- Full benchmark execution completed without changing benchmark assets.
- Gate 6B machine-readable parity, index identity, per-query, and aggregate
  artifacts are under `gate6b-results/`.
