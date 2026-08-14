# Gate 3 — C1 native pre-filter review

**Status:** bounded C1 implementation and execution proof complete; Gate 4 is
not started.

## Runtime boundary

C0 remains the existing H2 Dense path. C1 is the same Dense provider with a
validated `RetrievalContract` compiled into an Elasticsearch native `knn`
`filter`. The contract is supplied as a semantic object on `Query` (or an
equivalent plan parameter); arbitrary DSL never enters runtime. C1 reports
`strategy_identity=C1`, while no-contract execution reports `C0`.

## Supported and deferred scope

Runtime-enabled profile fields are industry, role, location, years_experience
and seniority. Seniority ordered comparisons use numeric `seniority_rank`.
Temporal, nested employer/client, relationship object/time,
delivery/advisory and prohibited-capability requirements remain deferred and
return explicit non-executable results. No text fallback or silent relaxation
is used.

## Correctness evidence

Against an isolated versioned v0.5 projection index on Elasticsearch 8.15.3:

- `years_experience >= 20` returned exactly D/E; 8/9/unknown did not match.
- `seniority >= senior` returned B/C/D/E using numeric rank 2.
- deterministic conjunctions are emitted as native bool filters.
- exclusions are emitted with `must_not` polarity.
- fewer eligible results than requested Top-K are returned without backfill;
  diagnostics expose strict shortfall.
- deferred temporal constraints produce an empty explicit non-executable result
  and no Elasticsearch request.

The no-contract C1-compatible call retains the unfiltered Dense payload, so C0
and C1 share the same embedding, similarity, ordering and Top-K semantics.

## Diagnostics and latency

Result provenance exposes strategy identity, contract ID, validation state,
hard/executable/non-executable counts, plan IDs, requested/returned counts,
shortfall count, and stage timings for contract validation, filter compilation,
Dense+filter execution and total retrieval.

## Limitations and Gate 4 questions

This is a small deterministic smoke/integration proof, not a C0/C1 quality
comparison or formal benchmark. Gate 4 must decide whether to run the formal
C0–C3 experiment, how to report candidate-set changes, and whether deferred
nested/temporal semantics should be expanded. Workbench and frontend paths were
not changed.
