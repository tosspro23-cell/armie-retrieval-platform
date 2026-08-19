# Gate 3I — Deterministic Span Proposal + Model Role Classification

**Status:** Candidate-complete / READY_FOR_FOUNDER_ACCEPTANCE
**Decision:** B — model-only Stage 2 improves some roles but remains insufficient
**Gate 4:** Inactive

Gate 3G-R was accepted with Decision B and Gate 3H was accepted with Decision
C. This study tests only the interface attribution question: fixed
deterministic Stage 1 spans followed by qwen3:8b role classification. The
valid Gate 3G-R held-out benchmark, ontology, Stages 3–6, C1, and Workbench
were unchanged.

## Frozen contracts

**Stage 1:** `deterministic-staged-span-proposal-v1` using the existing
`detect_spans` behavior. It proposes candidate text only.

**Stage 2:** one Ollama JSON object with exactly `{ "role": "<one of six roles>" }`.
The model receives the full request and supplied candidate phrase. It cannot
rewrite, split, shorten, or generate spans and cannot emit fields, operators,
values, offsets, or RetrievalContract objects.

## Development evidence

Fixture: `v0.5.1-gate3fr-staged-dev-validation-v1` (36 requests, role-only
truth, not Gate 3G-R gold). The deterministic Stage 1 produced 61 candidate
spans: 100% request-boundary validity, 100% containment match to annotated
semantic phrases, and zero duplicate span boundaries. Nested candidates (for
example, a phrase and an embedded registry token) are retained as an explicit
known limitation rather than silently removed.

Frozen development targets: False REQUIRED 0%, False EXCLUDED 0%, overall role
accuracy >=85%, REQUIRED/EXCLUDED >=85%, PREFERRED/CONTEXT_ONLY >=80%, and
UNSUPPORTED/AMBIGUOUS >=75%.

## Results

| Metric | Deterministic Stage 2 | qwen3:8b role-only |
|---|---:|---:|
| Completion coverage | 100% | 100% (61/61 spans) |
| Schema validity | deterministic | 100% |
| Overall role accuracy | 81.97% | 55.74% |
| False REQUIRED | 0% | 32.79% (20/61) |
| False EXCLUDED | 0% | 1.64% (1/61) |
| REQUIRED accuracy | 90.91% | 100% |
| EXCLUDED accuracy | 100% | 72.73% |
| PREFERRED accuracy | 76.92% | 100% |
| CONTEXT_ONLY accuracy | 100% | 18.18% |
| UNSUPPORTED accuracy | 66.67% | 0% |
| AMBIGUOUS accuracy | 44.44% | 0% |
| Mean / p50 / p95 latency | ~0.17 / 0.08 / 0.24 ms | 413.9 / 358.7 / 415.3 ms |
| Model calls | n/a | 61 (one per span) |

The role-only interface materially improves PREFERRED and REQUIRED recall
relative to the Gate 3H joint interface (0% role accuracy), but it remains
unsafe: contextual, unsupported, and ambiguous phrases are frequently
classified as REQUIRED. This fails the primary safety targets.

## Attribution and error taxonomy

Removing span generation removes the token-fragment failure observed in Gate
3H and yields valid JSON role outputs. It does not solve semantic scope:

- context → requirement: dominant failure (CONTEXT_ONLY 18.18% correct);
- unsupported → requirement: UNSUPPORTED 0% correct;
- ambiguity → requirement: AMBIGUOUS 0% correct;
- exclusion scope: one False EXCLUDED and 72.73% EXCLUDED accuracy;
- preference/requirement: PREFERRED is strong at 100%;
- conjunction/scope: represented in mixed/context examples and remains unsafe.

## Downstream diagnostic

All 36 model outputs were passed through the unchanged deterministic Stage 3–5
functions: 12 validated constraints, 0 validation errors. The role-only fixture
contains no gold field/operator/value contract, so mapping accuracy,
supported precision/recall, and final False-HARD are **not estimable** here and
are not fabricated.

## Repeatability

Six representative spans (REQUIRED, EXCLUDED, PREFERRED, CONTEXT_ONLY,
UNSUPPORTED, AMBIGUOUS) were each classified three times. The model was stable
within each span (e.g. REQUIRED/PREFERRED/EXCLUDED stayed stable), including
stable unsafe classifications of CONTEXT_ONLY, UNSUPPORTED, and AMBIGUOUS as
REQUIRED. No prompt iteration or tuning loop was performed.

## Decision and boundary

**Decision B:** model-only Stage 2 provides a real interface improvement over
Gate 3H but remains insufficient for a candidate architecture because its
False REQUIRED rate is 32.79% and contextual safety is poor. Do not create a
model-assisted promotion candidate, cascade, C1 integration, or Gate 4 work.
A future bounded gate would need to address scope-sensitive safety and
unsupported/ambiguous handling with a new contract and independently frozen
development evidence.

Machine evidence is retained in ignored `.artifacts/v051_gate3i_results.json`
and `.artifacts/gate3i-qwen8b-checkpoint.json`.
