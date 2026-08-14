# Gate 6M — Architecture Decision

**Decision: C — Do not promote C1 due to guardrail failure**

The prohibited-exclusion evaluator defect was repaired and validated without
changing the benchmark fingerprint, runtime, Dataset v2, or any other metric.
All 230 executions completed with the locked v1.1 benchmark.

C1 removed explicit hard violations and prohibited violations, but its NDCG@5
fell from 0.7256 (C0) to 0.2191, a 50.65 percentage-point degradation against
the frozen 5pp guardrail. It therefore cannot be promoted under the original
decision protocol.

C2-20, C2-50 and C2-100 did not produce a material eligible-recall advantage
over C1; C2 cost increased with N. C2 is de-prioritized. C3 remains deferred
because no complementary C1/C2 evidence was established.

Run 1 and Gate 6R remain historical invalid runs. Gate 6M is valid for this
metric-repair result and architecture decision, subject to the documented
synthetic benchmark limitations.
