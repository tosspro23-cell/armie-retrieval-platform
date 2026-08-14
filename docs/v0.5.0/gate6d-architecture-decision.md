# Gate 6D — Architecture Decision

**Decision: A — Promote C1, de-prioritize C2, keep C3 deferred.**

Under the newly frozen constraint-aware protocol, C1 satisfies the primary
objective: eligible NDCG, Precision, MRR, Recall, and Fill all improve over C0;
constraint violation and hard-negative intrusion are materially lower; native
projection parity is exact; and the 37 supply-sufficient query comparison has
no eligible-NDCG losses beyond the frozen tolerance. Warm p95 latency remains
within the 1.5× C0 bound.

Raw NDCG remains lower than C0, but it is explicitly diagnostic under this
protocol because unconstrained relevance rewards candidates that violate hard
constraints. This does not retroactively promote C1 under Gate 6M or Gate 6B;
it is a new protocol-governed decision.

C2-20/50/100 show no material incremental eligible gain and are de-prioritized.
C3 remains deferred.
