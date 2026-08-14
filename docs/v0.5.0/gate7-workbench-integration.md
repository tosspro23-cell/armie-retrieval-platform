# Gate 7 Workbench Integration

The existing Workbench remains the presentation layer over the frozen runtime.
Gate 7 adds disclosure rather than a new UI workflow:

- `/api/v1/capabilities` reports the promoted C1 strategy and registry;
- `/api/v1/constraints/registry` exposes supported fields/operators without
  backend DSL;
- benchmark manifest metadata identifies the configured v0.5 projection/index;
- result provenance and stage summaries remain available through the existing
  trace response;
- C0/C1 identity, unsupported state, index compatibility, and strict shortfall
  are explicit for clients to render.

The Workbench must not imply that temporal, relationship, delivery, or evidence
constraints execute natively. It must not present C2 candidate expansion or C3
as promoted runtime behavior. Historical H1/H3/H4 and Dataset v2 benchmark
artifacts remain unchanged.
