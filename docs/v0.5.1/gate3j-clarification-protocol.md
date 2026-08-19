# Gate 3J — Clarification Protocol & Intent Resolution

**Status:** Candidate-complete / READY_FOR_FOUNDER_ACCEPTANCE
**Decision:** Candidate architecture: uncertainty flows to clarification, not
autonomous hardening
**Gate 4:** Inactive

Gate 3I was accepted with Decision B. Gate 3J is protocol/foundation work only:
no Workbench UI, chat agent, C1 execution, model tuning, or benchmark changes.

## Clarification objects

`ClarificationItem` (`clarification-item-v1`) contains:
`clarification_id`, request identity, source span, surrounding context, current
state, bounded `ClarificationType`, allowed resolutions, deterministic question
and choices, provenance, dependency IDs, and lifecycle status.

`ClarificationResolution` (`clarification-resolution-v1`) contains the item ID,
selected resolution, optional corrected field/value or user text, source
(`user`), and sequence. It is authoritative for the current interpretation
session but is not executable by itself.

## Bounded taxonomy and policy

The six clarification types are `requirement_strength`, `exclusion_scope`,
`numeric_intent`, `category_attachment`, `unsupported_intent`, and
`reference_scope`.

High-confidence explicit phrases such as “must have at least 20 years”,
“exclude Financial Services”, and “preferably based in London” bypass
clarification. Keyword presence alone is not sufficient. Possible hard
requirements, exclusions, numeric eligibility, and unsupported meanings that
could affect execution are blocking. Pure context and clearly bounded soft
preferences may remain non-blocking, but are still preserved in provenance.
Unresolved risk transitions to `NEEDS_CLARIFICATION`; it never silently becomes
REQUIRED or EXCLUDED.

## Lifecycle and state machine

```text
RAW → INTERPRETED → INTERPRETATION_COMPLETE → NEEDS_CONFIRMATION
                         ↑          ↓                 ↓
                 NEEDS_CLARIFICATION              CONFIRMED
                                                        ↓
                                             VALIDATED_CONTRACT
```

Blocking clarification items must be resolved before confirmation. The no-
clarification fast path goes directly to `INTERPRETATION_COMPLETE`, then still
requires confirmation. Clarification and confirmation are separate operations.

`UNRESOLVED → NEEDS_CLARIFICATION → RESOLVED` is the normal item lifecycle;
`CANCELLED` represents removal or dependency invalidation. Unknown IDs and
double resolution are rejected unless an explicit `edit=True` operation is
provided. Edits append provenance, invalidate dependent items where required,
and force reconfirmation.

## Resolution and authority

Applying a resolution is deterministic and records the user source. Choosing
REQUIRED for unsupported relationship meaning does not create an executable
constraint or expand C1 support; registry/schema validation remains mandatory.
`REMOVE_FROM_CONSTRAINT_INTERPRETATION` preserves the original phrase in
provenance while cancelling its derived clarification and dependents.

The same `ClarificationItem`/`ClarificationResolution` contract is suitable for
a future structured Workbench or conversational adapter. Gate 3J does not
implement either presentation layer. Batch-vs-one-at-a-time ordering is an
adapter decision; dependency-aware invalidation is core protocol behavior.

## Fixtures and invariants

The deterministic test suite covers no-clarification fast path, requirement
strength, numeric/exclusion taxonomy, multiple items, supported plus
unsupported meaning, remove, edit, dependency invalidation, unknown IDs,
confirmation separation, provenance, and unsupported-resolution safety.
No model calls, C1 execution, or UI execution are part of this evidence.

Future evaluation should measure unsafe autonomous hardening, clarification
recall, unnecessary clarification, clarification turns, and user correction
rate. A future Workbench clarification/confirmation UX Gate is the next
possible product boundary, subject to Founder authorization.
