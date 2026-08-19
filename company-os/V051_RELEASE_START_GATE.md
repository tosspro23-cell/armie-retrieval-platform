# v0.5.1 Release Stabilization and Closeout — Start Gate

**Work Object ID:** `armie-retrieval-v051-release-stabilization-closeout`
**Status:** active / Founder-authorized
**Project ID:** `armie-retrieval-platform`
**Core reference:** ARMIE Company OS Core v0.1; this repository's
[`PROJECT_ADAPTER.md`](PROJECT_ADAPTER.md) is the project adapter.

## Objective

Validate and publish the frozen v0.5.1 capability, then write the verified
release state back to the Project OS. This is release stabilization and
closeout, not a new implementation gate.

## Frozen scope

v0.5.1 adds governed natural-language intent resolution before the existing
v0.5.0 deterministic C1 substrate:

`natural-language request → interpretation → clarification when needed → user
resolution → confirmation → RetrievalContract → existing C1 → Elasticsearch
results and provenance`.

The release does not claim unrestricted autonomous semantic-role
interpretation, conversational clarification, unsupported relationship or
temporal semantics, autonomous execution without confirmation, C1 ranking
redesign, Dataset v2 changes, or v0.6 functionality.

## Authority and evidence profile

The Founder explicitly accepted Gate 5 and the Gate 5-F/F2/F3 fixes, froze the
v0.5.1 capability boundary, and authorized release/GitHub publish/closeout.
Gate evidence is [the Gate 5 Result Package](../docs/v0.5.1/gate5-confirmed-c1-e2e.md).

Before publishing, distinguish these fact layers:

| Layer | Current fact at activation |
|---|---|
| Local candidate | v0.5.1 implementation, tests, docs, and governance records are uncommitted. |
| Committed | `main` is v0.5.0 closeout `f181960`. |
| Remote | `origin/main` is `f181960`. |
| Tag | no `v0.5.1` tag exists at activation. |
| GitHub Release object | no v0.5.1 object exists at activation. |
| Founder acceptance | Gate 5 and v0.5.1 release are accepted/authorized. |

## Allowed work

- audit/classify the worktree and exclude generated or unrelated content;
- correct release metadata, release documentation, and Company OS records;
- run required validation and real-runtime smoke evidence;
- create bounded commits, annotated tag `v0.5.1`, push `main` and tag;
- attempt a GitHub Release object only with available authenticated tooling;
- reconcile verified post-push facts and close this Work Object.

## Explicit exclusions

No new product features, Stage 1/2 tuning, clarification-semantic change, C1
change, ranking/relevance change, Dataset v2 or benchmark change,
conversational agent, v0.6 activity, force-push, or tag rewrite.

`docs/v0.4.0/post-release-closeout.md` is historical, uncommitted material
outside the v0.5.1 release payload; preserve it unmodified and do not stage it.

## Acceptance criteria and stop condition

Required: full Python suite, focused v0.5.1 checks, frontend tests/build, live
Founder-critical Playwright, C1 smoke, Dataset/index identity, package build,
link and diff checks, clean release staging, committed/tagged/pushed refs, and
post-push Company OS reconciliation.

Stop immediately if validation fails, remote authentication is unavailable,
the target tag conflicts, or any release-content classification becomes
ambiguous. Do not start v0.6 after closeout.
