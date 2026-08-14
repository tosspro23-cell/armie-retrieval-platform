# Gate 6R — Architecture Decision

**Decision:** D — evidence remains invalid/inconclusive

The repaired v1.1 benchmark identity and lineage validated successfully, and
all 230 frozen arm executions completed. However, the result calculator used
`not eligible` as a proxy for explicit prohibited-exclusion violation. This
does not satisfy the frozen definition of Prohibited Constraint Violation@5,
which requires a candidate to violate an explicit exclusion. Because the
defect was discovered after results were observed, Gate 6R stops without
repairing or rerunning the benchmark.

Run 1 remains separately preserved and invalid for its semantic-query and
exclusion-serialization defects. Gate 6R is also not valid for architecture
promotion due solely to this result-calculation defect.

C1/C2 observations, latency, raw per-query traces and environment identity are
preserved in [`gate6r-results/`](gate6r-results/). No arm is promoted, C2 is
not retained on this evidence, and C3 remains deferred.
