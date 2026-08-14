# ARMIE Retrieval Platform v0.5.0 — Gate 5 Architecture Selection

**Status:** Architecture and benchmark-design freeze only; no Gate 6 execution

**Scope boundary:** This document records the selection decision after Gate 4B.
It does not authorize a new runtime capability, C3, a Dataset mutation, a
formal benchmark, a Workbench change, a commit, a tag, or a push.

## 1. Frozen architecture arms

| Arm | Definition | Gate 6 role |
|---|---|---|
| **C0** | Released H2 Dense baseline | Primary control |
| **C1** | H2 Dense plus deterministic native pre-filter | Primary constraint arm |
| **C2-20** | H2 Dense candidate pool of 20 plus deterministic post-filter | Secondary low-cost experiment |
| **C2-50** | H2 Dense candidate pool of 50 plus deterministic post-filter | Secondary intermediate-pool experiment |
| **C2-100** | H2 Dense candidate pool of 100 plus deterministic post-filter | Secondary recall-oriented upper bound |
| **C3** | Hybrid native pre-filter plus post-verification | **Deferred** |

H1, H3 and H4 remain historical v0.4 references only. They are not part of
the primary v0.5 constraint axis and will not be modified.

## 2. C3 decision

C3 is deferred by evidence, not permanently rejected. Gate 4B found:

- no tested case where C2 recovered an eligible candidate missed by C1;
- identical C1/C2 Top-5 results once C2 reached sufficient eligible candidates;
- increasing C2's pool increased candidate and end-to-end cost;
- the currently supported constraints are deterministic and index-ready; and
- no complementary C1/C2 failure mode was demonstrated that justifies hybrid
  complexity.

Future temporal, relationship, delivery/evidence or natural-data findings may
reopen the C3 hypothesis through a new architecture decision. C3 must not be
implemented or inferred from the Gate 6 design.

## 3. Why C2 remains as a secondary arm

Gate 4B did not show a quality win for C2, but it did expose useful engineering
information: strict shortfall under selective contracts, candidate-pool
saturation, and the cost of deterministic verification. C2 therefore remains
only as three pre-registered secondary arms (N=20, 50, 100), rather than all
five exploratory Gate 4B pool sizes. These represent low-cost, intermediate
and recall-oriented observations without turning the formal experiment into a
pool-size sweep.

C2 may be de-prioritized after Gate 6 if it still produces no eligible result
that C1 misses and its added cost is material. It is not a default path.

## 4. Preserved corpus and release boundaries

Gate 6 must use the immutable Dataset v2 full corpus:

- manifest: `v2-realism-full`;
- profiles: 10,000;
- checksum: `514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`.

The released v0.4.0 benchmark (103 Gold / 17 Silver) remains immutable. The
v0.5 constraint extension is a separate versioned query/judgement layer over
the same profiles. No Dataset v3 is created.

## 5. Supported semantic boundary

The Gate 6 core may exercise the deterministic runtime scope already proven by
Gates 1–4: numeric, categorical, role/seniority, location and explicit
negative constraints. Temporal, nested employer/client, relationship
object/time, delivery/advisory and prohibited-capability semantics remain
deferred unless separately approved and supported by the current runtime.

## 6. Post-Gate-6 decision rules

- **Promote C1** when constraint correctness materially improves over C0,
  relevance and eligible recall stay within guardrails, latency is acceptable,
  and no systematic false exclusion is found.
- **Retain C2** only when it recovers materially useful eligible results or
  eligible recall not recovered by C1, with a cost justified by that gain.
- **Drop or de-prioritize C2** when C1/C2 quality is effectively equivalent,
  C2 recovers no additional eligible results, and C2 costs more.
- **Reopen C3** only when Gate 6 demonstrates complementary C1/C2 strengths
  or a newly approved constraint class cannot be safely handled by C1 alone.

These are pre-registered decision rules, not Gate 6 results.

## 7. Evidence boundary

Gate 4B was a bounded engineering smoke experiment on Elasticsearch 8.15.3
using an isolated 100-document v0.5 projection fixture. It was not formal
benchmark evidence and made no statistical claims. The full results and
limitations are recorded in
[`gate4b-candidate-pool-smoke.md`](gate4b-candidate-pool-smoke.md).

No Gate 6 benchmark has been run under this freeze.
