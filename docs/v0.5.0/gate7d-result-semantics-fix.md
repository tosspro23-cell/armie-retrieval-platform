# Gate 7D — Final Result Semantics and Constraint Evidence

## Scope

Gate 7D is a bounded correctness and presentation fix on the already accepted
C1 Workbench path. It does not change the retrieval contract, Dataset v2,
indexing, H1/H3/H4, or the free-query C0/H2 path. No Gate 8 or release work is
included.

## Root cause and reproduction

The structured endpoint requested a dense candidate pool of 100 (`retrieval_candidate_k=100`) while the product request was `requested_k=5`. The Elasticsearch retriever exposed those hits directly as `results` and reported the pool length as `returned_k`; there was no separate candidate-pool/eligible/final-result accounting. A reproducible pre-fix response therefore returned 100 rows for a requested Top-5 query and made the strict shortfall/provenance fields ambiguous.

## Corrected contract

The retriever now keeps the Elasticsearch response as an internal candidate
pool, slices it to `plan.top_k`, and returns only that final list. Native C1
filtering means the returned pool is eligible, but the quantities are reported
separately:

| Field | Meaning |
|---|---|
| `requested_k` | User-requested final Top-K |
| `candidate_pool_count` | Hits returned by the dense candidate request |
| `eligible_candidate_count` | Candidates remaining after native C1 filtering |
| `returned_k` | Final result rows returned to the caller |
| `shortfall` | `requested_k - returned_k` when positive |

The same values are present in `constraint_diagnostics`, and `returned_k` is
never greater than `requested_k`. No candidate-pool backfill is performed.

## Live threshold evidence

Against the compatible Gate 6B Elasticsearch dense index (`BAAI/bge-m3`, 1024
dimensions), a temporary local API was run with the current source and then
stopped cleanly. Each request asked for five results and used only a structured
`years_experience >= threshold` contract.

| Threshold | Returned IDs (years) | Candidate pool | Eligible | Returned | Shortfall |
|---:|---|---:|---:|---:|---:|
| 10 | `expert-v2-01153` (20), `expert-v2-01023` (20), `expert-v2-01027` (18), `expert-v2-09343` (20), `expert-v2-09213` (20) | 100 | 100 | 5 | 0 |
| 20 | `expert-v2-01153` (20), `expert-v2-00163` (20), `expert-v2-01023` (20), `expert-v2-03025` (24), `expert-v2-01203` (20) | 100 | 100 | 5 | 0 |
| 25 | `expert-v2-08758` (25), `expert-v2-05248` (25), `expert-v2-05428` (25), `expert-v2-01738` (25), `expert-v2-07588` (25) | 100 | 100 | 5 | 0 |

The first row demonstrates the threshold semantics rather than a typo: 18 is
valid for `>=10`. The `>=20` and `>=25` rows contain only values satisfying
their respective thresholds. The live browser path also verified a strict
1000-year starvation case with zero results and an explicit shortfall.

## Structured result evidence

Every C1 result now exposes structured facts for:

- years experience;
- seniority;
- industries;
- roles;
- locations.

For every required or excluded constraint, the response includes a
`constraint_evidence` row with the canonical field, operator, expected value,
observed candidate value, polarity, and `SATISFIED`, `VIOLATED`, or `UNKNOWN`
state. The Workbench renders these rows as **Constraint Evidence**, including
required seniority/industry combinations and explicit “must not match”
exclusions. This is explanatory evidence for the executable contract, not a
new evaluator or a claim of external human ground truth.

## Regression boundaries

- Free queries remain C0/H2 Dense and unlabelled.
- Unsupported/deferred contracts remain explicit and do not fall back to C0.
- C1 remains native Elasticsearch pre-filtering; no C2/C3 behavior changed.
- H1/H3/H4, Dataset v2, benchmark metrics, and Workbench benchmark semantics
  are unchanged.

## Validation

- Gate 7D-focused Python tests: 10 passed.
- Full Python suite: 131 passed, 3 skipped (with the repository's existing
  ignored-artifact write permission).
- Elasticsearch integration: 2 passed against the available cluster.
- Frontend unit tests: 4 passed.
- Focused live Gate 7C/7D browser suite: 8 passed.
- Full Playwright suite: 29 passed.
- Frontend production build: passed.
- Package/import checks and `git diff --check`: passed.

Manual visual acceptance remains a founder decision; Gate 8 and release work
remain out of scope.
