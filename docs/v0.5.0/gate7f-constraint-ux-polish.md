# Gate 7F — Constraint UX Polish

**Status:** bounded UX polish complete; no retrieval architecture, benchmark,
Dataset v2, C1/C0 semantics, or Gate 8 work changed.

## Product-language contract

The Workbench now separates:

- **Semantic query** — describes who the user is looking for and drives Dense
  relevance retrieval.
- **Must-have filters** — explicit deterministic eligibility requirements
  enforced by C1 native pre-filtering.

The helper copy states that text in the semantic query is not automatically
converted into filters. Natural-language-to-contract extraction remains out of
scope for v0.5.

## Registry-backed controls

Industry and excluded-industry are now controlled selects. Their canonical
values come from `/api/v1/constraints/registry`; the frontend does not maintain
a second vocabulary. Human labels are rendered while canonical values such as
`healthcare` and `financial services` are submitted unchanged. Years remains a
numeric control and seniority remains an explicit controlled selector. The
unsupported/deferred scenario remains visibly marked test-only.

## Strategy and evidence presentation

With structured mode off, the Workbench shows **Dense / H2** and executes C0.
With structured mode on, it shows **Constraint-aware Dense (C1)** and the
relationship **Base retriever: H2 Dense · Constraint strategy: native
pre-filter**. The contract summary uses product language such as “Experience:
at least 20 years”, “Industry: Healthcare”, and “Exclude industry: Financial
Services”. Canonical operators remain available in diagnostics/provenance.

Constraint Evidence keeps the Gate 7D per-result facts and now uses aligned
wording such as “Required: Industry: Healthcare” and “must not match”. C0
results show ordinary profile industry facts but no constraint evidence or
constraint summary.

## Founder scenarios verified

The live founder path was exercised against the existing frontend on 5173 and
the restarted repository backend on 8000:

1. Semantic-only healthcare query remained C0/H2 and returned a non-healthcare
   profile, demonstrating that semantic text alone is not a hard filter.
2. Adding the Healthcare registry value produced a valid C1 contract and no
   non-Healthcare leakage. The live Gate 6B projection currently contains only
   Financial Services and Manufacturing industry values, so this environment
   correctly returned a strict shortfall of zero rather than fabricating a
   populated Healthcare example.
3. Years >= 20 returned five visible results with matching evidence.
4. Healthcare + years >= 20 + Senior or above displayed and enforced all
   selected filters.
5. Exclude Financial Services rendered “must not match” and returned no
   Financial Services candidate.

## Validation

- Frontend unit tests: 5 passed.
- Live founder Playwright Gate 7C/7F scenarios: 9 passed.
- Frontend production build: passed.
- Backend registry endpoint: canonical industry values verified.
- Existing targeted backend C1 tests: 10 passed before this presentation-only
  change; runtime contract semantics were not modified.
- Markdown links: 78 documents checked, 0 missing.
- `git diff --check`: passed.

The remaining founder-owned manual checks are visual density, copy clarity,
perceived latency on the actual device, and a populated Healthcare positive
case if a compatible projection containing Healthcare is provisioned. Gate 7F
is ready for final founder acceptance review; Gate 8, commit, tag, and push
remain out of scope.
