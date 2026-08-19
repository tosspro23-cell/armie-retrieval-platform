# v0.5.1 Gate 4 — Clarification & Confirmation Workbench

**Status:** Candidate-complete; `READY_FOR_FOUNDER_ACCEPTANCE`
**Scope:** bounded Workbench integration of the accepted Gate 3J protocol

Gate 4 connects the deterministic clarification protocol to a structured
Workbench review surface. It does not execute C1, promote an extractor, add a
conversational agent, or change the existing retrieval architecture.

## Frozen user flow

```text
Natural language query
        ↓
Interpretation review
        ↓
NEEDS_CLARIFICATION (when ambiguity is detected)
        ↓
User selects a bounded resolution
        ↓
INTERPRETATION_COMPLETE
        ↓
Explicit Confirm interpretation
        ↓
VALIDATED_CONTRACT
```

The no-clarification path still requires explicit confirmation. A validated
contract is a hand-off boundary for a future, separately authorized C1 call;
this Gate 4 panel never executes retrieval.

## Backend contract

The typed API is exposed under `/api/v1`:

- `POST /interpret` creates an isolated interpretation session.
- `GET /interpretations/{session_id}` reads current state.
- `POST /interpretations/{session_id}/resolutions` applies a permitted choice.
- `PUT /interpretations/{session_id}/resolutions` edits a prior choice.
- `POST /interpretations/{session_id}/confirm` performs confirmation and
  deterministic contract validation.

Invalid session IDs, unknown clarification IDs, and disallowed choices return
typed Workbench errors. Resolution provenance and sequence are retained by the
Gate 3J protocol. The edit route preserves explicit revision semantics, while
`REMOVE_FROM_CONSTRAINT_INTERPRETATION` and dependency cancellation remain
typed protocol outcomes rather than hidden UI inference. Retrieval run state is
unchanged by these endpoints.

## Workbench behavior

The **Interpretation review** card is intentionally structured rather than
conversational. **Review intent** creates a session; ambiguity cards show the
source span, question, and bounded choices. **Confirm interpretation** is only
shown after all blocking clarifications are resolved. The final state explicitly
reports `VALIDATED_CONTRACT` and its future-C1 boundary.

The existing C0/C1 controls, exclusion display, unsupported-state messaging,
provenance, metrics, and result views remain unchanged. No hard constraint is
silently inferred from free text, and no C1 fallback is introduced.

## Verification evidence

- `tests/test_v051_gate3j_clarification.py` — protocol lifecycle and safety.
- `tests/test_v051_gate4_workbench.py` — service and typed API state flow,
  invalid resolution handling, confirmation boundary, and no-retrieval proof.
- `apps/workbench/tests/workbench.test.js` — deterministic UI marker coverage.

Gate 4 validation runs the default Python suite, focused protocol/API tests,
frontend tests, frontend production build, Markdown link checks, and
`git diff --check`. Live browser/Elasticsearch acceptance remains a Founder
review activity and is not claimed here.

## Founder review checklist

1. Review an unambiguous query and observe `INTERPRETATION_COMPLETE`.
2. Review an ambiguous query such as “around 20 years” and select a bounded
   resolution.
3. Confirm that no retrieval executes while resolving or confirming.
4. Confirm that `VALIDATED_CONTRACT` is visible as a boundary, not a result.
5. Confirm that existing C0/C1 controls and provenance remain understandable.

Gate 5 and autonomous C1 execution remain inactive until the Founder accepts
this Result Package and explicitly authorizes the next work object.
