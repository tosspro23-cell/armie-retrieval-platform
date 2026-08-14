# Gate 4B — C1/C2 candidate-pool smoke experiment

**Gate 4B engineering smoke experiment — not formal benchmark evidence**

No C3, Gate 5, formal Gate 6 benchmark, Dataset mutation, v0.4 index change,
Workbench change, commit, tag or push was performed.

## Environment and fixture

- Elasticsearch: 8.15.3
- Isolated temporary versioned v0.5 projection index; deleted after the run
- 100 deterministic projection documents and a fixed unit query vector
- Top-K: 5
- C2 candidate pools: 10, 20, 30, 50, 100
- Runtime paths: C0 H2 Dense, C1 native pre-filter, C2 Dense pool + post-filter

## C1 baseline results

| Case | C1 returned IDs | Returned | Shortfall |
|---|---|---:|---:|
| years >= 20 | E004,E008,E012,E016,E020 | 5 | 0 |
| industry Energy | E003,E006,E009,E012,E018 | 5 | 0 |
| seniority >= senior | E001,E004,E003,E006,E007 | 5 | 0 |
| Energy + years >=20 + seniority >= senior | E012,E024,E036,E048,E072 | 5 | 0 |
| Engineer + exclude Banking | E002,E004,E006,E008,E012 | 5 | 0 |
| Rare high-selectivity | E095 | 1 | 4 |

## C2 results

Each row is a separate explicit-N execution; there was no hidden pool
expansion. `sat/viol/unk` are candidate-level verification states.

| Case | N | Retrieved | sat/viol/unk | Eligible | Returned | Shortfall | Returned IDs | E2E ms |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| years >=20 | 10 | 10 | 2/8/0 | 2 | 2 | 3 | E004,E008 | 3.658 |
| years >=20 | 20 | 20 | 5/15/0 | 5 | 5 | 0 | E004,E008,E012,E016,E020 | 11.743 |
| years >=20 | 30 | 30 | 7/23/0 | 7 | 5 | 0 | E004,E008,E012,E016,E020 | 6.514 |
| years >=20 | 50 | 50 | 12/38/0 | 12 | 5 | 0 | E004,E008,E012,E016,E020 | 7.399 |
| years >=20 | 100 | 100 | 25/75/0 | 25 | 5 | 0 | E004,E008,E012,E016,E020 | 10.850 |
| industry Energy | 10 | 10 | 3/7/0 | 3 | 3 | 2 | E003,E006,E009 | 3.587 |
| industry Energy | 20 | 20 | 5/15/0 | 5 | 5 | 0 | E003,E006,E009,E012,E018 | 4.123 |
| industry Energy | 30 | 30 | 8/22/0 | 8 | 5 | 0 | E003,E006,E009,E012,E018 | 4.890 |
| industry Energy | 50 | 50 | 13/37/0 | 13 | 5 | 0 | E003,E006,E009,E012,E018 | 6.475 |
| industry Energy | 100 | 100 | 27/73/0 | 27 | 5 | 0 | E003,E006,E009,E012,E018 | 12.000 |
| seniority >= senior | 10 | 10 | 7/3/0 | 7 | 5 | 0 | E001,E004,E003,E006,E007 | 4.200 |
| seniority >= senior | 20 | 20 | 13/7/0 | 13 | 5 | 0 | E001,E004,E003,E006,E007 | 4.500 |
| seniority >= senior | 30 | 30 | 20/10/0 | 20 | 5 | 0 | E001,E004,E003,E006,E007 | 5.711 |
| seniority >= senior | 50 | 50 | 33/17/0 | 33 | 5 | 0 | E001,E004,E003,E006,E007 | 7.197 |
| seniority >= senior | 100 | 100 | 67/33/0 | 67 | 5 | 0 | E001,E004,E003,E006,E007 | 10.184 |
| multi-constraint | 10 | 10 | 0/10/0 | 0 | 0 | 5 | — | 4.076 |
| multi-constraint | 20 | 20 | 1/19/0 | 1 | 1 | 4 | E012 | 4.592 |
| multi-constraint | 30 | 30 | 2/28/0 | 2 | 2 | 3 | E012,E024 | 5.153 |
| multi-constraint | 50 | 50 | 4/46/0 | 4 | 4 | 1 | E012,E024,E036,E048 | 7.117 |
| multi-constraint | 100 | 100 | 7/93/0 | 7 | 5 | 0 | E012,E024,E036,E048,E072 | 11.506 |
| Engineer - exclude Banking | 10 | 10 | 4/1/0 | 4 | 4 | 1 | E002,E004,E006,E008 | 4.109 |
| Engineer - exclude Banking | 20 | 20 | 8/2/0 | 8 | 5 | 0 | E002,E004,E006,E008,E012 | 4.616 |
| Engineer - exclude Banking | 30 | 30 | 12/3/0 | 12 | 5 | 0 | E002,E004,E006,E008,E012 | 4.835 |
| Engineer - exclude Banking | 50 | 50 | 20/5/0 | 20 | 5 | 0 | E002,E004,E006,E008,E012 | 6.460 |
| Engineer - exclude Banking | 100 | 100 | 40/10/0 | 40 | 5 | 0 | E002,E004,E006,E008,E012 | 10.431 |
| Rare high-selectivity | 10 | 10 | 0/10/0 | 0 | 0 | 5 | — | 3.230 |
| Rare high-selectivity | 20 | 20 | 0/20/0 | 0 | 0 | 5 | — | 4.240 |
| Rare high-selectivity | 30 | 30 | 0/30/0 | 0 | 0 | 5 | — | 5.299 |
| Rare high-selectivity | 50 | 50 | 0/50/0 | 0 | 0 | 5 | — | 6.896 |
| Rare high-selectivity | 100 | 100 | 1/99/0 | 1 | 1 | 4 | E095 | 10.870 |

## Findings

1. C2 correctness is preserved on real Elasticsearch-backed execution. C2
   candidate retrieval is intentionally unconstrained Dense; verification then
   uses canonical structured metadata and keeps Dense order.
2. C2 did not find useful eligible candidates that C1 missed. Once C2 reached
   five eligible results, its returned IDs matched C1 in every tested case.
   Smaller pools produced subsets or starvation, never a better eligible set.
3. Apparent saturation was case-dependent: years reached Top-5 at N=20,
   industry at N=20, seniority at N=10, the conjunction at N=100, and the Rare
   case never filled Top-5 even at N=100.
4. Verification cost was small (roughly 0.03–0.60 ms in these runs), while
   Dense/E2E cost generally grew with N (roughly 3–12 ms). These are raw smoke
   timings, not distributional claims.
5. C1 and C2 were frequently identical at the returned Top-5 once the C2 pool
   saturated. C2 adds candidate materialization and verification cost without
   observed recovery beyond C1 in this fixture.

## Recommendation

De-prioritize C2 for the formal Gate 6 benchmark unless a larger, explicitly
approved experiment identifies a C1 miss that C2 recovers. C3 is not warranted
by this smoke experiment. This recommendation is not a statistical superiority
claim; it is a bounded engineering observation.

## Tests and skipped tests

- Gate 4 focused tests: 5 passed.
- Full Python suite: 97 passed, 3 skipped.
- `test_dense_vector_mapping_is_indexed` — environment-gated v0.4 ES test;
  skipped unless `ARMIE_RUN_ELASTICSEARCH_INTEGRATION=1`.
- `test_pinned_cluster_and_index_are_available` — same environment gate.
- `test_h1_to_h4_execute_through_shared_runtime` — formal v0.4 integration
  gate; not part of Gate 4B.

No formal H1–H4 or C0–C3 benchmark, Playwright, Workbench test, commit, tag or
push was performed.
