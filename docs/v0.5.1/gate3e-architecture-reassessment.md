# Gate 3E — Failure Decomposition & Architecture Reassessment

**Status:** Candidate-complete; ready for Founder acceptance
**Version:** ARMIE Retrieval Platform v0.5.1
**Scope:** Architecture and evidence review only. No extractor, prompt, benchmark,
threshold, dataset, runtime, C1, Workbench, Gate 4, commit, tag, or push changes
were made in Gate 3E.

## Decision summary

Gate 3D is treated as accepted evidence with architecture decision D: no
extractor is promoted. Gate 4 remains inactive. Gate 3E closes the requested
failure decomposition and recommends a staged interpretation architecture as
the next design direction, subject to Founder acceptance.

## Development versus frozen evidence

| Evidence slice | Arm | False HARD | Exact | Precision | Recall |
|---|---|---:|---:|---:|---:|
| Gate 2 development | Rule development | 0.00% | 75.00% | 100.00% | 95.00% |
| Gate 3 frozen | Rule v2 | 9.17% | 28.33% | 66.25% | 62.78% |
| Gate 3D frozen | Rule v3 | 6.67% | 24.17% | 59.58% | 55.00% |
| Gate 3D frozen | Model v2 | 0.00% | 0.00% | 30.00% | 30.00% |
| Gate 3D frozen | Cascade v2 | 6.67% | 23.33% | 59.58% | 55.00% |

The development slice is narrow and optimistic relative to the frozen 120-item
contract. It is useful for iteration, not for promotion evidence.

## Failure decomposition

The principal Rule failures are structural: mention versus requirement,
description versus eligibility, contextual entity versus candidate property,
negation scope, delivery/relationship requirements, and conjunction/paraphrase.
More pattern patches would reduce individual examples without removing this
architecture ceiling.

The model path is operationally valid (120/120 structured outputs, zero False
HARD, and bounded repeatability) but conservative: exact 0%, precision 30%, and
recall 30%. The evidence does not indicate an infrastructure or adapter fault.
The result is consistent with task decomposition, schema/policy complexity,
and model capacity/abstention limits.

## One-shot complexity diagnosis

The current one-shot contract asks one pass to detect spans, infer intent,
map ontology, normalize operators, and assemble a constrained interpretation.
That coupling explains both rule brittleness and model under-selection. The
model's zero False HARD is valuable safety evidence, not evidence of useful
coverage.

## Recommended staged architecture

```text
span detection
  -> intent class (REQUIRED / EXCLUSION / PREFERENCE / UNSUPPORTED /
                  AMBIGUOUS / CONTEXT_ONLY)
  -> registry mapping
  -> operator normalization
  -> deterministic validation
  -> contract assembly
```

This makes intermediate evidence inspectable, permits deterministic safety
checks, and isolates model use to bounded interpretation decisions. It adds
schema and evaluation work, but does not require a runtime or C1 redesign.

## CONTEXT_ONLY and ontology

`CONTEXT_ONLY` should be an interpretation-layer class for text that provides
context but must not become a candidate eligibility constraint. It is not a
new C1 runtime semantic.

The current HARD/SOFT distinction is too coarse for safe interpretation. A
future schema should distinguish `REQUIRED`, `EXCLUDED`, `PREFERRED`,
`CONTEXT_ONLY`, `UNSUPPORTED`, and `AMBIGUOUS`, with explicit evidence and
confidence. Existing benchmark fields and thresholds remain frozen until a
new contract is approved.

## Stronger model timing and scope

Do not test a stronger model as the first response. First establish the staged
baseline and its development diagnostics. A stronger model can then be tested
as a controlled variable against the same frozen contract. The v0.5.1 interim
scope should be explicit-requirement-only where safety requires it, with
unsupported or ambiguous language surfaced rather than silently promoted.

## Options considered

| Path | Assessment |
|---|---|
| A — staged interpretation | **Preferred primary path.** Makes failure boundaries measurable. |
| B — stronger one-shot model | Defer until staged baseline; otherwise diagnosis remains confounded. |
| C — narrow explicit-requirement-only | Viable interim safety boundary, not a complete solution. |
| D — defer all work | Unnecessary if scope is reduced and evidence remains development-only. |

## Benchmark governance

The current 120-item benchmark remains frozen diagnostic evidence. It must not
be silently rewritten as a post-redesign promotion set. A prospective held-out
set should be specified before any staged implementation is promoted.

Future evaluation should report span detection precision/recall, intent-class
accuracy, False REQUIRED and CONTEXT_ONLY rates, preference/exclusion handling,
registry field/value mapping, operator normalization, and final False HARD,
exact, precision, recall, unsupported, and contradiction metrics. Thresholds
remain unchanged; any new promotion thresholds require a separately approved
contract.

## Proposed next gate (not started)

**Gate 3F — Staged Interpretation Architecture Design and Development
Validation.** Its scope would be design, interfaces, development fixtures, and
failure-boundary evidence only. It must not replace the frozen benchmark,
promote an extractor, modify C1/Workbench behavior, or start Gate 4 without a
new Founder decision.

## Limitations and provenance

All figures above are transcribed from the Gate 2/Gate 3/Gate 3D artifacts;
they are controlled synthetic benchmark evidence, not production quality or
external human-ground-truth evidence. Gate 3E performed no model calls and no
code or benchmark mutation. See [Gate 3D semantics refinement](gate3d-semantics-refinement.md)
and [v0.5.1 validation report](../v0.4.0/validation-report.md).
