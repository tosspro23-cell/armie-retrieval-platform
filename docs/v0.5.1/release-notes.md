# ARMIE Retrieval Platform v0.5.1

## Highlights

- Governed natural-language constraint interpretation on top of the v0.5.0
  deterministic C1 retrieval substrate.
- Bounded clarification protocol for unsafe or ambiguous supported intent.
- Explicit user resolution and final confirmation before natural-language
  derived C1 execution.
- Workbench clarification/confirmation UX and confirmed interpretation →
  canonical `RetrievalContract` → existing C1 execution.
- Execution provenance, stale-session/contract protection, and distinct
  not-executed, executed-zero, and executed-with-results rendering.

## Safety boundary

- Uncertainty never silently becomes `REQUIRED` or `EXCLUDED`.
- Preferred and context-only information does not become a hard constraint.
- Unsupported meaning cannot fabricate registry or C1 support.
- Editing an interpretation invalidates prior confirmation and results.
- User clarification resolves only the bounded supported choices; it does not
  expand runtime capability.

## Compatibility

- Existing v0.5.0 manual structured C1 remains supported.
- Existing H2 Dense unconstrained semantic retrieval remains supported.
- C1 ranking/relevance behavior, Dataset v2, projection identity, and benchmark
  protocol are unchanged.

## Validation boundary

The release was validated against the local controlled-synthetic Dataset v2
runtime and the compatible Elasticsearch 8.15.3 C1 projection. This is runtime
and safety evidence, not validation of natural expert-network quality or
unrestricted natural-language understanding.

## Deferred

- Conversational clarification.
- Unrestricted autonomous semantic-role interpretation.
- Broader temporal, relationship, delivery, and evidence semantics.
- Healthcare positive-coverage expansion in the current projection.
- Founder-startup convenience tooling beyond the existing local launcher.
