# Gate 7B — Founder / Manual Acceptance Checklist

This checklist is intentionally not pre-marked as passed. Automated evidence
is recorded separately in `gate7b-live-e2e.md`; the founder should inspect the
live UI before accepting Gate 7B.

## Manual checks

- [ ] Page loads correctly at the intended local UI port.
- [ ] Dense and Constraint-aware Dense/C1 are visually distinguishable.
- [ ] Contract summary clearly separates required constraints and exclusions.
- [ ] Supported fields/operators are understandable without exposing raw DSL.
- [ ] Unsupported/deferred constraints identify the category and do not imply
      that retrieval was fully enforced.
- [ ] Strict shortfall reads as a normal strict-contract outcome, not an
      application failure (for example, “returned 3 of requested 5”).
- [ ] Returned results contain no ineligible backfill.
- [ ] Each structured result shows candidate facts and per-constraint evidence
      (including exclusions) in a human-readable form.
- [ ] Provenance is useful: strategy, contract state, plan IDs, index/projection
      identity, counts, shortfall, and latency are visible without misleading
      product claims.
- [ ] Latency feels acceptable for a local development run.
- [ ] No UI text overclaims temporal, relationship, delivery, evidence,
      arbitrary natural-language, C2, or C3 support.
- [ ] No obvious visual regressions in Workbench, Query Lab, evidence, audit,
      verification, or raw-trace views.

## Current review status

The page-load and free-query H2 presentation were inspected live. The page
rendered correctly; H2 results showed `Dense score`, runtime diagnostics, and
“Quality evaluation unavailable” for the unlabelled free query. The remaining
constraint-aware browser checks were subsequently exercised by the Gate 7C
Playwright suite through the live structured-contract-to-Elasticsearch path.
Those automated results are recorded in `gate7c-live-acceptance.md`; the
visual/manual items above remain intentionally unchecked.

## Acceptance decision

Founder decision required: accept or reject Gate 7B/7C live integration after
reviewing the automated evidence and inspecting the unchecked visual items.
