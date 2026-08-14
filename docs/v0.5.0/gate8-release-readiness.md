# Gate 8 — v0.5.0 Release Readiness

**Status:** release candidate prepared; no commit, tag, push, or GitHub release
was created in this gate.

## Release scope and isolation

The current worktree contains accumulated Gate 1–7 implementation and evidence
plus Company OS changes. The intended v0.5.0 release scope is deterministic and
must be staged by explicit path, not by staging the whole worktree.

| Classification | Paths |
|---|---|
| A — v0.5.0 required runtime | `src/armie_retrieval/contracts.py`, `src/armie_retrieval/constraints/`, `src/armie_retrieval/indexing/constraint_projection.py`, `src/armie_retrieval/retrievers/c2_postfilter.py`, `src/armie_retrieval/application/workbench.py`, `src/armie_retrieval/providers/elasticsearch/retrievers.py`, `services/api/app.py`, `services/api/schemas.py`, `src/armie_retrieval/__init__.py`, `pyproject.toml`, `setup.cfg`, `apps/workbench/package.json`, `apps/workbench/package-lock.json`, Workbench source/styles |
| A — v0.5.0 tests/tools | `tests/test_v050_*.py`, `tests/test_workbench_api.py`, `scripts/build_v050_gate6b_index.py`, `scripts/gate6d_protocol.py`, `scripts/materialize_v050_constraint_extension*.py`, `scripts/run_v050_gate6.py`, `apps/workbench/tests/gate7c.integration.spec.ts`, `apps/workbench/tests/workbench.test.js`, Playwright configuration/spec updates |
| B — v0.5.0 evidence/docs | `docs/v0.5.0/`, `README.md`, `CHANGELOG.md`, and the release manifest/notes/readiness files |
| C — unrelated/preserved | `company-os/` and `docs/v0.4.0/post-release-closeout.md`; these remain unstaged for a v0.5 release commit |
| D — generated/local | `.artifacts/`, `dist/`, `apps/workbench/dist/`, `apps/workbench/node_modules/`, Playwright reports/results, `.DS_Store`, and egg-info outputs; all ignored and excluded |
| E — uncertain | None after review; historical v0.4 documents remain historical evidence rather than current release identity |

The unrelated Company OS work is preserved in place. A future release should
use explicit `git add` path groups (or a temporary clean worktree) and inspect
the staged diff before committing; it must not use `git add .`.

## Architecture lineage and final capability

v0.4.0 is the relevance-engineering baseline. v0.5.0 is constraint-aware
retrieval. The final capability is:

> ARMIE Retrieval Platform v0.5.0 supports deterministic structured
> hard-constraint expert retrieval over an approved field scope using native
> pre-filtered Dense retrieval with strict no-relaxation semantics.

Supported fields are `years_experience`, `industry`, `role`, `location`,
`seniority`, approved explicit exclusions, and approved conjunctions. C0 is H2
Dense for unconstrained semantic retrieval. C1 is the promoted default
constraint path. C2 is diagnostic/de-prioritized. C3 is deferred. The release
does not claim arbitrary NL-to-contract extraction, general temporal or
relationship reasoning, delivery/evidence qualification, graph retrieval, or
production C2/C3 support.

## Reproducibility identity

| Artifact | Identity |
|---|---|
| Dataset | `v2-realism-full`, checksum `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc` |
| Benchmark | `v0.5-constraint-extension-v1.1`, fingerprint `6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb` |
| Evaluation protocol | `v0.5-constraint-aware-eval-protocol-v1`, fingerprint `7cfc4945cb81bfe145dc1d80d0e936f9e1e4d9bdc521f7254113cb4405156e12` |
| Projection | `constraint-projection-0.2-gate6b`, mapping fingerprint `e7f3acf23f2d90964e4e771da14bb033b93d386a6e73c4d351a91a40cfba5a0d` |
| Embedding | `BAAI/bge-m3`, 1024 dimensions |
| Registry | `v0.5-c1-capability-registry-1` |
| Elasticsearch | 8.15.3; compatibility checks require the projection schema and required fields |

The runtime currently selects the configured compatible dense index through
`ARMIE_V050_C1_INDEX`; the default local name remains
`armie-experts-v1-v2-gate6b-dense-10000`. A stable release alias is a future
infrastructure review item, not a silent Gate 8 migration.

## Gate 6D evidence

| Metric | C0 | C1 |
|---|---:|---:|
| Eligible NDCG@5 | 0.3027 | 0.4917 |
| Eligible P@5 | 0.2913 | 0.4913 |
| Eligible MRR | 0.4019 | 0.5897 |
| Eligible Recall@10 | 0.0120 | 0.0211 |
| Eligible Fill@5 | 0.3622 | 0.6108 |
| Constraint Violation@5 | 0.6130 | 0 |
| Hard-negative intrusion@5 | 0.4174 | 0 |

Paired eligible NDCG was **21 wins / 16 ties / 0 losses** over 37
supply-sufficient queries. C2 showed no material eligible-quality improvement
over C1 and incurred higher latency, so it is de-prioritized. The raw relevance
diagnostic remains visible: C0 raw NDCG@5 = 0.7286 versus C1 raw NDCG@5 =
0.4917. Raw relevance rewards relevant-but-ineligible candidates and is not the
promotion criterion.

Earlier invalid/inconclusive runs are preserved as governance history: Gate 6
had query/relevance alignment and exclusion serialization defects; Gate 6R had
a prohibited-violation evaluator defect; Gate 6M corrected evaluation but
exposed projection mismatch; Gate 6A decomposed the failure; Gate 6B repaired
the projection; Gate 6D froze the constraint-aware protocol and promoted C1.

## Port debt resolution

Gate 6 Playwright API tests now use `ARMIE_WORKBENCH_API_URL`, then the existing
`ARMIE_WORKBENCH_URL`, with the isolated 8782 service as the default. The
Playwright configuration supports explicit founder frontend/backend URLs via
`PLAYWRIGHT_FRONTEND`, `PLAYWRIGHT_BACKEND`, and `PLAYWRIGHT_FOUNDER_ENV=1`.
Canonical isolated and focused founder suites therefore run without relying on
an undocumented hardcoded port. The prior founder run's 8782 failures were
test-harness configuration debt, not product failures.

## Version consistency

Release-facing package metadata is aligned at `0.5.0` in `pyproject.toml`,
`setup.cfg`, the Python package, Workbench `package.json`/lockfile, API
metadata, and Workbench display/response surfaces. Remaining `v0.4.0`
references are historical changelog, README, benchmark, or test-module
identifiers and are not current product-version claims.

## Final validation matrix

- Python full suite: **131 passed, 3 skipped** (three skips are optional real
  Elasticsearch/Gate 4 integration tests when the opt-in environment is not
  set).
- Targeted Gate 1–7 Python suites: passed.
- Elasticsearch-enabled integration: **2 passed** with
  `ARMIE_RUN_ELASTICSEARCH_INTEGRATION=1` against the local Elasticsearch 8.15.3
  service.
- Frontend unit: **5 passed**.
- Frontend production build: passed.
- Canonical isolated Playwright: **30 passed**.
- Founder-environment full Playwright suite: **30 passed** (including the
  nine live Gate 7 C0/C1 scenarios) with explicit frontend/backend URLs.
- Python package build: passed.
- Import smoke, Markdown links, and `git diff --check`: passed.

## Proposed commit, tag, and release plan (not executed)

1. `feat(v050): add constraint-aware retrieval foundation` — explicit runtime,
   contract, projection, registry, and targeted test paths.
2. `feat(workbench): productize C1 constraint evidence` — Workbench source,
   styles, tests, and Playwright configuration/specs.
3. `docs(v050): prepare release candidate` — README, CHANGELOG, Gate 8 docs,
   release notes/manifest, and v0.5 evidence.

Company OS and v0.4 closeout paths remain unstaged. Intended tag: `v0.5.0`.
Intended release title: `v0.5.0 — Constraint-Aware Retrieval`. Release body:
`docs/v0.5.0/v0.5.0-release-notes.md`. A future release sequence must run the
final matrix, stage only the explicit groups, commit, create the annotated tag,
push branch and tag, then verify remote commit/tag and any GitHub Release object
separately.

## Remaining issues

- **KNOWN-LIMITATION:** the current Gate 6B projection contains Financial
  Services and Manufacturing values; a populated Healthcare positive example
  requires a compatible projection containing Healthcare.
- **SHOULD-FIX:** replace the temporary dense index default with a stable
  release alias after separate infrastructure review.
- **NON-RELEASE:** natural-language extraction, temporal/relationship/delivery
  semantics, C2/C3, ANN tuning, and v0.6 work.

No unexplained product test failure remains in the canonical validation matrix.
The repository is ready for a controlled v0.5.0 release commit, but this Gate 8
task intentionally stops before staging, committing, tagging, or pushing.
