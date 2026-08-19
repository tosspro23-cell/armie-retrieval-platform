# v0.5.1 Gate 5 — Confirmed Interpretation to C1

**Status:** Gate 5-F candidate-complete / `READY_FOR_FOUNDER_RETEST`
**Scope:** execution-boundary integration only; no semantic tuning or C1 redesign

## Architecture

```text
Natural language → interpretation → clarification → confirmation
→ VALIDATED_CONTRACT → existing RetrievalContract validator/compiler/C1
→ Elasticsearch constrained retrieval → evidence/provenance
```

Manual structured controls and the confirmed interpretation path converge at the
same `RetrievalContract` boundary. No model participates in final compilation.
`PREFERRED` and `CONTEXT_ONLY` remain non-executable; unsupported meaning stays
visible and blocks Gate 5 execution rather than being fabricated as a predicate.

## Execution boundary

The backend requires `VALIDATED_CONTRACT` and the current contract fingerprint
for `POST /api/v1/interpretations/{session_id}/execute`. RAW,
`NEEDS_CLARIFICATION`, `INTERPRETATION_COMPLETE`, unconfirmed, edited, and stale
contracts are rejected. A confirmed interpretation with no hard constraints
uses the existing H2 semantic-only path (C0-equivalent), never a fabricated C1.

The bridge reuses the existing `RetrievalContract`, deterministic validator,
native Elasticsearch pre-filter, strict shortfall behavior, and provenance
response. It does not create a second constraint engine.

## API and evidence

- `POST /api/v1/interpret` creates an isolated session.
- `POST/PUT /api/v1/interpretations/{id}/resolutions` applies or edits a
  bounded user resolution.
- `POST /api/v1/interpretations/{id}/confirm` creates and validates the
  canonical contract.
- `POST /api/v1/interpretations/{id}/execute` verifies state/fingerprint and
  invokes existing C1 (or C0-equivalent when no hard constraints remain).

After `VALIDATED_CONTRACT`, Workbench exposes an explicit **Search with
confirmed constraints** action. Confirmation alone does not trigger retrieval;
the action sends only the session reference and current contract fingerprint.

Execution errors are typed for unconfirmed, stale, unsupported, invalid, and
unavailable execution states. Contract provenance includes the source span,
resolution ID, contract ID, and current session identity.

## Validation evidence

- `tests/test_v051_gate4_workbench.py` covers confirmation rejection,
  confirmed execution binding, stale fingerprints, and edit invalidation.
- `tests/test_v051_gate3j_clarification.py` preserves Gate 3J lifecycle safety.
- Existing Workbench API, C1, strict-shortfall, and v0.5.0 regression tests are
  retained.

## Live runtime verification (bounded evidence)

The standard Elasticsearch service was started with
`docker compose -f docker-compose.elasticsearch.yml up -d` (Docker 29.7.2).
Health was green on Elasticsearch 8.15.3. The logical alias
`armie-experts-v0.5-dense` resolved to
`armie-experts-v1-v2-gate6b-dense-10000` with 10,000 documents. Mapping and
projection identity were accepted by the C1 compatibility check:
BAAI/bge-m3, 1024 dimensions, `constraint-projection-0.2-gate6b`, and the
recorded v2-realism-full lineage/checksum.

The backend was started with the repository-supported command
`PYTHONPATH=src python3 -m uvicorn services.api.app:app --host 127.0.0.1
--port 8000`; the Workbench used `npm run dev -- --host 127.0.0.1 --port
5173`. Health, capabilities, and constraint-registry endpoints returned 200.
Structured C1 execution reached Elasticsearch and returned provenance,
contract diagnostics, strict shortfall fields, and result IDs. Observed
scenarios included:

| Scenario | Result |
|---|---|
| no contract / H2 | 5 legacy-fixture results; C0/H2 path; unlabelled |
| years >= 10 | 5 C1 results; native filter; 100 candidates/100 eligible |
| seniority >= senior | 5 C1 results; native filter; 100/100 |
| manufacturing + years >= 10 | 5 C1 results; native filter; 100/100 |
| manufacturing exclusion | 5 C1 results; exclusion trace and provenance |
| years >= 1000 | 0 results; strict shortfall 5; no backfill |
| before confirmation | typed `interpretation_not_confirmed` rejection |
| unsupported `worked at Acme` | typed `unsupported_executable_intent`; no retrieval |
| all hard constraints removed | H2 semantic-only path; 5 results |

The ambiguous `around 20 years` flow was resolved as `MINIMUM`, confirmed, and
executed through C1 with 5 results. A manual structured contract with the same
numeric/category constraints produced the same C1 contract shape and result
behavior; the comparison is unlabelled runtime equivalence, not a quality
claim.

The initial live Gate 7C browser file was 8/9 while the v2 payload was absent.
After the canonical restoration below, the exact rerun completed 9/9. The
broader browser suite was not used as Gate 5 evidence because its default API
target is 8782. No new Gold/Silver metric claim is made by this runtime-parity
task.

## Founder Test Script

1. `Find Healthcare experts with at least 20 years of experience, excluding
   Financial Services.` — no clarification; confirm; execute; inspect C1
   evidence and exclusions.
2. `Find senior AI experts with around 20 years of experience.` — resolve the
   numeric ambiguity as `MINIMUM`, confirm, then execute.
3. Try Search before confirmation — expect a typed rejection.
4. Edit a confirmed resolution — expect confirmation invalidation; reconfirm.
5. Use `worked at Acme` — unsupported relationship remains visible and does
   not become a fake C1 predicate.
6. Remove or soften all hard constraints — expect semantic-only C0-equivalent
   behavior.
7. Use a high-selectivity supported constraint — verify strict shortfall and
   no ineligible backfill.
8. Start a new interpretation session — previous contract and results must
   not be reusable.

## Gate 5-R parity closure

The missing runtime payload was restored by invoking the repository's
canonical `build_v2_pilot` generator with the approved full-corpus parameters:
10,000 profiles, 120 queries, seeds 7301/9137, and `v2-realism-full`. No
Dataset v2 source, judgement truth, index, or runtime code was changed. The
generated artifact reports checksum
`514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`, query set
`expert-discovery-queries-v2-realism-0.2`, and judgement set
`expert-discovery-judgements-v2-structured-0.2`.

With `ARMIE_V2_BENCHMARK_ROOT=/tmp/armie-v040-dataset-v2-full`, the Workbench
reports `Expert Discovery v2`, `benchmark_v2_available=true`, and default
profile H2. The exact Gate 5 browser command completed **9 passed, 0 failed**.
The representative confirmed-NL path still returns C1 with 5 results and
`constraint_prefilter`; an unconfirmed execution still returns typed
`interpretation_not_confirmed`. Legacy v1 fallback is eliminated for this
runtime. Gate 5 is now **READY_FOR_FOUNDER_MANUAL_TEST**; this does not accept
Gate 5 or authorize Gate 6.

Founder manual execution is pending. Gate 6/release work remains inactive.

## Gate 5-F founder integration fix (bounded)

Founder testing identified three integration defects without changing the
interpretation taxonomy, Dataset v2, C1 semantics, or retrieval tuning:

- **F1 — governed execution bypass:** the generic `/query` path could execute
  while an interpretation session was unresolved or unconfirmed. The backend
  now routes an active interpretation session through the canonical governed
  executor, so unresolved and unconfirmed sessions are rejected and confirmed
  sessions execute the stored validated contract. Manual structured retrieval
  without an active natural-language session remains available.
- **F2 — misleading clarification status:** the Workbench now displays the
  backend-sourced `blocking_clarification_count` and a resolution prompt rather
  than claiming that no clarification is blocking while a clarification is
  unresolved.
- **F3 — action hierarchy and review order:** Interpretation Review is placed
  after Semantic Query; the generic Run retrieval action is disabled while a
  governed session is active, leaving clarify → confirm → execute as the only
  available natural-language path. Query/mode changes invalidate the session,
  governed state, and stale results.

### Exact Founder case

`Find healthcare experts with Azure AI experience around 20 years` now follows
the bounded state sequence `NEEDS_CLARIFICATION` → resolve `around` as
`MINIMUM` → `INTERPRETATION_COMPLETE` → explicit confirmation →
`VALIDATED_CONTRACT` → existing C1 execution. Before resolution or confirmation
the generic action is disabled and backend execution is rejected with the typed
`interpretation_not_confirmed` error. The live browser path completed this case
through confirmed C1.

### Gate 5-F validation

- Targeted backend protocol suite: 12 tests passed (including legacy-query
  bypass and canonical C1 routing guards).
- Frontend unit/static suite: 6 tests passed; production build passed.
- Live Gate 7C integration suite, including the exact Founder case: **10 passed,
  0 failed** against the restored v2 payload and Elasticsearch-backed backend.
- `git diff --check`: passed.

Gate 5-F is candidate-complete and ready for Founder retest. It does not accept
Gate 5, authorize Gate 6, or change release state.

## Gate 5-F2 — governed Search flow and exact Founder-case diagnosis

Gate 5-F2 is a bounded integration repair for F4/F5. It does not change the
Stage 1/2 interpretation taxonomy, the C1 compiler/runtime, Dataset v2, or the
Gate 6 boundary.

### F4 — primary Search is governed in C1 mode

When the Workbench is in governed/Constraint-aware Dense mode, the primary
Search action now calls the governed query boundary. A fresh natural-language
query is first interpreted and returns `execution_status=blocked`; it cannot
create a retrieval run. An ambiguous query reaches `NEEDS_CLARIFICATION`, an
unambiguous query reaches `INTERPRETATION_COMPLETE` with confirmation required,
and only a confirmed session can execute the stored contract through C1.
Explicit manual structured fields remain available and continue to call the
existing `/structured-query` path. Non-governed H2 remains the explicit semantic
mode.

The focused backend suite now covers fresh governed ambiguous and unambiguous
queries, no-run guarantees, and confirmed-session C1 routing. The browser suite
covers primary Search without Review, clarification resolution, confirmation,
and confirmed C1 execution.

### F5 — exact Founder query lineage and zero-result explanation

The exact query was executed against the live alias
`armie-experts-v0.5-dense`, resolved to physical index
`armie-experts-v1-v2-gate6b-dense-10000`:

`Find healthcare experts with Azure AI experience around 20 years`

The observed lineage is:

1. `around 20 years` → numeric clarification → `MINIMUM`.
2. Candidate interpretation → `industry=healthcare` and
   `years_experience >= 20` as hard constraints.
3. Confirmation → `VALIDATED_CONTRACT` (`v0.5.0-contract-1`).
4. C1 native dense pre-filter → 0 eligible candidates, 0 returned, strict
   shortfall 5, with `filter_applied=true` and `constraint_prefilter`.

The index identity reported compatible projection metadata:
`armie-v0.5-constraint-projection-v1`, implementation
`constraint-projection-0.2-gate6b`, mapping `expert-discovery-es-mapping-v2-gate6b`,
`BAAI/bge-m3`, 1024 dimensions. Direct read-only Elasticsearch checks found
2,307 profiles with `years_experience >= 20`, 0 with `industries=healthcare`,
and 0 satisfying the combined predicate. The live index industry distribution
is 5,000 `financial services` and 5,000 `manufacturing` profiles. Thus the
zero result is explained by the accepted hard industry predicate and current
projection contents, not by a fabricated success or a retrieval fallback.

The confirmed natural-language contract and an equivalent manual structured
contract both return 0. A years-only manual contract returns 5, proving the
healthcare predicate is the limiting condition. No semantic retuning was made
to force a non-zero result; the natural-language/manual equivalence and the
data/projection limitation are recorded for Founder review.

### Gate 5-F2 validation and candidate state

- Focused backend protocol suite: 15 tests passed (including governed fresh
  query blocking, confirmation boundary, and canonical C1 routing).
- Frontend unit suite and production build: passed.
- Live browser coverage: governed primary Search, clarification/confirmation,
  manual structured C1, and non-governed H2 paths; exact F5 zero-result case
  remains reproducible against the current alias/index.
- `git diff --check`: passed.

Gate 5-F2 is **candidate-complete / READY_FOR_FOUNDER_RETEST_2**. The F5
zero-result behavior is an explicit data/projection finding, not a semantic
repair or a claim of real-world relevance. Gate 5 remains unaccepted and Gate
6 remains inactive.

## Gate 5-F3 — confirmed execution result rendering

### F6 diagnosis

The confirmed interpretation execution endpoint already returned the complete
`WorkbenchResponse` shape: `results`, `answer_summary`, `stage_summaries`,
`evidence`, `verification`, `metrics`, `execution_context`, and trace data.
The defect was frontend state divergence. Manual structured execution wrote its
response to the Workbench `response` state, while confirmed execution wrote
only to the InterpretationPanel's local `executed` state. Consequently the
local panel displayed “Execution complete” but the canonical Answer Summary,
Results, Audit, Evidence, Metrics, and Execution Context still read as if no
execution had occurred.

### Bounded repair

The InterpretationPanel now emits the existing confirmed execution response to
the Workbench's canonical `response` state through an `onExecution` boundary.
The existing panels render that same response; NL clarification/confirmation
lineage remains visible in the interpretation panel. No backend response schema,
retrieval semantics, Dataset v2, or C1 behavior changed.

The result lifecycle is now explicit in the UI:

- before execution: initial/no current execution state;
- successful execution with results: canonical response with exactly the
  backend result count rendered as result cards;
- successful execution with zero results: canonical response with zero cards,
  answer summary and strict-shortfall evidence still rendered;
- query or interpretation changes: response state is cleared before the next
  execution.

### F6 validation

- Exact Founder query `Find experts with Azure AI experience around 20 years`:
  backend returned 5 results and the Workbench rendered 5 result cards.
- Answer Summary, C1 audit/provenance, Metrics, and Execution Context populated
  from the same response.
- Exact valid zero-result case with healthcare plus `MINIMUM`: backend returned
  0 and the Workbench rendered 0 cards while preserving the executed answer and
  shortfall (`returned 0 of 5 requested`).
- Manual structured C1 paths remain covered by the existing live regression.
- Focused backend suite: 17 tests passed; frontend unit suite: 6 passed;
  production build passed; complete live Playwright suite: 14 passed; `git
  diff --check` passed.

Gate 5-F3 is **candidate-complete / READY_FOR_FOUNDER_RETEST_3**. F4 is
Founder-verified closed; F6 is repaired and validated. Gate 5 remains
unaccepted and Gate 6 remains inactive.

## Founder-critical Playwright verification

This focused verification reused the live local services and the compatible
Elasticsearch 8.15.3 alias `armie-experts-v0.5-dense`, which resolves to
`armie-experts-v1-v2-gate6b-dense-10000` (10,000 documents; `BAAI/bge-m3`;
1,024 dimensions). The versioned Dataset v2 root was
`/tmp/armie-v040-dataset-v2-full`, with manifest version
`v2-realism-full` and checksum
`514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`.

The exact live command was:

```text
PLAYWRIGHT_FOUNDER_ENV=1 PLAYWRIGHT_FRONTEND=http://127.0.0.1:5173 PLAYWRIGHT_BACKEND=http://127.0.0.1:8000 ARMIE_WORKBENCH_API_URL=http://127.0.0.1:8000 ARMIE_V2_BENCHMARK_ROOT=/tmp/armie-v040-dataset-v2-full npx playwright test tests/gate7c.integration.spec.ts --reporter=line
```

**Result: 16 passed, 0 failed, 0 skipped.** The suite verified the governed
natural-language path, the explicit C1 path, and the Workbench rendering
boundary against the live backend and Elasticsearch index:

- the Founder Azure AI / `around 20 years` query required clarification,
  `MINIMUM`, confirmation, then returned and rendered five C1 results;
- the healthcare plus `MINIMUM` case executed as a valid zero-result response,
  rendered zero cards, and retained the strict shortfall; no relaxation or
  ineligible backfill occurred;
- unresolved and resolved-but-unconfirmed interpretations did not execute or
  silently bypass to C0;
- editing an already confirmed interpretation retired the prior execution and
  required reconfirmation; a new session cleared its prior result state;
- manual structured C1, exclusion, seniority, multi-constraint, strict
  shortfall, unsupported-contract, provenance, and capability paths remained
  covered.

For the positive and zero-result cases, visible result-card counts matched the
backend response counts (five and zero respectively). The suite separately
covers no-execution, executed-zero, and executed-with-results states. This is
automated candidate evidence sufficient for a Founder acceptance review; it
does **not** itself accept Gate 5 or authorize Gate 6.
