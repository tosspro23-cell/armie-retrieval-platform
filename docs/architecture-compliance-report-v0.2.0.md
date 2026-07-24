# Architecture Compliance Report — v0.2.0

**Authority:** [Architecture Freeze v1.0](architecture-freeze-v1.md)
**Assessment:** Compliant, with explicitly documented MVP boundaries.

| ADR | Status | Evidence |
|---|---|---|
| ADR-001: Declarative planning | Implemented | `RetrievalPlan` holds strategy, processors, filters, parameters, and constraints; it has no provider, SDK, index, or API fields. |
| ADR-002: Execution never changes the plan | Implemented | `RetrievalPlan` is frozen; runtime, retrievers, and processors consume but do not mutate it. |
| ADR-003: Planner knows capabilities, not implementations | Implemented | Planners receive capability sets; `RetrievalRuntime` resolves concrete retrievers through a registry. |
| ADR-004: Unified result envelope | Implemented | Retrievers return `RetrievalResult`; all processors take and return that type. |
| ADR-005: Learning updates policy, not runtime context | Implemented | `LearningEngine` consumes the offline `ObservationStore` and publishes immutable policies. Runtime has no observation-store dependency. |
| ADR-006: Learning is a platform capability | Partially implemented by design | The shared observation/policy contracts are component-agnostic. v0.2 policy rules currently act on capability and latency observations; evaluation-to-observation aggregation is deferred. |
| ADR-007: Registry and learning are independent | Implemented | Separate retriever, processor, and provider registries do discovery/resolution only; learning owns observations and policies. |

## No architecture changes

This release adds implementation detail and release metadata only. It does not alter the frozen component responsibilities, domain-object flow, or runtime/learning separation.
