# Architecture Compliance Report — v0.3.0

| Frozen decision | Status | Evidence |
|---|---|---|
| Declarative planner output | Implemented | Workbench delegates to existing planner and exposes its parsed plan. |
| Execution never mutates plans | Implemented | Queries call `RetrievalRuntime` unchanged. |
| Capability/implementation separation | Implemented | Existing profile and registry selectors remain the execution boundary. |
| Unified retrieval result | Implemented | API projects the existing `RetrievalResult` and trace. |
| Learning is offline | Preserved | No workbench request reads historical learning state. |
| Learning is platform-wide | Preserved | No new runtime learning path was introduced. |
| Registry and learning are independent | Implemented | The API does not register sessions, traces, or index artifacts. |

The Workbench is an application projection and does not introduce a second retrieval pipeline, provider registry, planner, or ranking implementation.
