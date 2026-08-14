# Gate 6B — Architecture Diagnosis

**Primary result: C — Projection repair succeeds, eligible retrieval is
healthy, but the raw-NDCG guardrail remains incompatible with hard-constraint
utility.**

Projection parity is exact and all 85 Gate 6A diagnostic candidates pass the
repaired native predicates. C1 Eligible Recall, Eligible Fill, and
eligible-conditioned ranking improve materially. The repaired C1 still has
raw NDCG@5 of 0.4917 versus repaired C0 at 0.7286, exceeding the frozen
5-percentage-point guardrail. Its paired comparison is 4 wins, 18 ties, and
24 losses, so C1 is not promoted under the original protocol.

This is not a C1 projection defect and does not justify changing the frozen
metrics or thresholds. The appropriate next step is a separately
pre-registered eligible-conditioned evaluation protocol. A Gate 6C
filtered-ANN study is **not warranted at this point**: the projection repair
removed the dominant eligible-retrieval failure, and C2 showed no incremental
aggregate benefit.

No runtime architecture, Dataset v2, benchmark fingerprint, C2 semantics, C3,
Workbench, or Gate 7 state was changed.
