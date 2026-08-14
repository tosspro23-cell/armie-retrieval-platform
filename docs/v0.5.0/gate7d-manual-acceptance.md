# Gate 7D — Manual Acceptance Checklist

This is a bounded founder review of final result semantics. Automated tests do
not mark these visual checks as accepted.

- [ ] A structured years query returns no more than five result cards.
- [ ] When five eligible profiles exist, exactly five cards are shown.
- [ ] A strict starvation query says “returned 0 of 5” (or the observed strict
      shortfall) and does not show ineligible backfill.
- [ ] Each result shows Years experience, Seniority, Industry, Role, and
      Location facts.
- [ ] **Constraint Evidence** is readable per result and shows candidate fact,
      operator, expected value, and state.
- [ ] Multi-constraint evidence visibly includes every required constraint.
- [ ] Exclusion evidence visibly explains the prohibited condition as “must
      not match”.
- [ ] Provenance distinguishes requested K, candidate pool, eligible count,
      returned K, and shortfall.
- [ ] Free-query C0/H2 remains unchanged and does not show structured evidence.
- [ ] No visual copy implies unsupported temporal/relationship execution.

## Gate 7E founder-environment verification

The checklist was exercised against the founder's existing services on
5173/8000. The live evidence and two bounded integration fixes are recorded in
[`gate7e-founder-environment-validation.md`](gate7e-founder-environment-validation.md).
Automated browser checks passed 8/8, including C0, C1, multi-constraint,
exclusion, unsupported, strict shortfall, and provenance. The remaining boxes
above are still founder-owned visual acceptance items; automated evidence does
not silently mark them accepted.

## Automated evidence references

- `gate7d-result-semantics-fix.md`
- `gate7c-live-acceptance.md`
- `gate7b-manual-acceptance-checklist.md`
- `gate7e-founder-environment-validation.md`

## Gate 7F UX evidence

`gate7f-constraint-ux-polish.md` records the distinction between semantic query
and deterministic must-have filters, registry-backed industry controls, C0/C1
strategy identity, and human-readable contract/evidence language.

Founder acceptance of Gate 7D and authorization for any later gate remain
pending.
