# ARMIE Retrieval Platform v0.5.0 Post-Release Closeout

**Release date:** 2026-08-14

**Release:** `v0.5.0 — Constraint-Aware Retrieval`

## Release identity

The controlled release sequence completed with these commits:

1. `5425b2e` — `feat(v050): add constraint-aware retrieval foundation`
2. `a42789d` — `feat(workbench): productize C1 constraint evidence`
3. `0102cdb` — `docs(v050): prepare release candidate`
4. `05e661f` — `test: stabilize founder free-query assertion`

Annotated tag `v0.5.0` has tag object `b4230aeeeb03aed1df57105db8f1d6c758af8251`
and targets release commit `05e661f7da0947aee9fa15a9e635fc602ac53626`.

Remote verification confirmed:

- Release tag target: `05e661f7da0947aee9fa15a9e635fc602ac53626`
- Final local `main`: `f181960ecefb2ccb025cf4bf83c21e9b8aa864de`
- Final `origin/main`: `f181960ecefb2ccb025cf4bf83c21e9b8aa864de`
- `origin/v0.5.0` → the immutable release commit above

The final closeout file is intentionally a follow-up documentation commit; the
annotated release tag is not amended or recreated.

## Validation

- Python: 131 passed, 3 optional skips
- Elasticsearch integration: 2 passed against Elasticsearch 8.15.3
- Workbench unit tests: 5 passed
- Workbench build: passed
- Canonical isolated Playwright: 30 passed
- Founder-environment Playwright: 30 passed
- Python package build: `armie_retrieval_platform-0.5.0` wheel and sdist passed
- Import smoke, Markdown links, and `git diff --check`: passed

## Architecture decision

- C0 remains H2 Dense for unconstrained semantic retrieval.
- C1 is the promoted default: H2 Dense plus deterministic native pre-filter.
- C2 remains diagnostic/de-prioritized.
- C3 remains deferred.

Only approved structured deterministic constraints are supported. The release
does not claim arbitrary natural-language extraction, general temporal,
relationship, delivery/evidence, or graph reasoning.

## Reproducibility identities

- Dataset: `v2-realism-full`
- Projection: `constraint-projection-0.2-gate6b`
- Benchmark: `v0.5-constraint-extension-v1.1`
- Evaluation protocol: `v0.5-constraint-aware-eval-protocol-v1`
- Registry: `v0.5-c1-capability-registry-1`
- Embedding: `BAAI/bge-m3` / 1024 dimensions

## Release limitations and deferred scope

Dataset v2 remains a controlled synthetic relevance benchmark. The populated
Gate 6B projection has limited industry coverage, and the temporary dense index
name remains a separate infrastructure follow-up for stable aliasing.

Natural-language contract extraction, deferred constraint semantics, C2/C3
production support, ANN tuning, and v0.6 work remain outside this release.

## GitHub Release object

The annotated Git tag and branch push succeeded. GitHub CLI is unavailable in
the engineering environment, and an unauthenticated GitHub Releases API lookup
returned `404`; therefore no GitHub Release object was created or claimed.

## Residual local work

The Company OS documentation changes and `docs/v0.4.0/post-release-closeout.md`
remain local and intentionally outside the v0.5.0 release commits.

## Next-version boundary

The next version must begin with a new Company OS Work Object and explicit
founder authorization. No v0.6 work is included in this release.
