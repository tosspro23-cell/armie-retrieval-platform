# Current Work Object — Gate 5.5A Decision

**Work Object:** `armie-retrieval-gate-5.5a-dataset-v2-pilot`  
**State:** completed result; awaiting founder decision  
**Authority:** founder acceptance required for any transition

## Objective

Validate whether a more diverse Dataset v2 design is ready to justify a later
full stability benchmark, without changing Dataset v1 or running the next gate.

## Scope and constraints

Included profile/document generation, independent query generation, canonical
truth-based draft judgements, relationship/temporal/evidence validation,
diversity/leakage diagnostics, and a bounded pilot audit.

Excluded full H1–H4, Query Lab/Gate 6, Gate 7, release preparation, tagging,
pushing, and any replacement of Dataset v1.

## Acceptance evidence

- 750-profile pilot, 40 queries across all ten categories, 30,000 judgements.
- Normalized-summary duplicate rate: 1.47%, below the <5% pilot target.
- Shared three-token query/document phrase overlap: 0; lower than the v1 pilot.
- Invalid temporal records: 0; projects outside employment intervals: 0.
- Positive judgement evidence coverage: 100%.
- Default Python suite: 63 passed, 3 skipped.
- Dataset v2 tests: 6 passed.
- Elasticsearch integration tests: 2 passed.
- Frontend tests/build and package build passed.
- `git diff --check` passed.

## Actual result

Gate 5.5A is a completed controlled synthetic relevance benchmark pilot. It is
not production-realistic and does not establish real-world expert-search quality.
The current implementation and documentation remain uncommitted in the shared
worktree.

## Candidate transition

**Proposed only:** activate Gate 5.5B for full Dataset v2 generation, stability
benchmarking, and explicit v1/v2 comparison.

## Founder decision required

The founder must explicitly accept or reject the candidate transition. No agent
may treat this result package as authorization to start Gate 5.5B.
