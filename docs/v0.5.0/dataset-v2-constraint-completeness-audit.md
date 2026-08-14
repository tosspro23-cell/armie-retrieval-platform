# Dataset v2 constraint-field completeness audit

**Gate:** 1.5 (read-only)
**Corpus:** `v2-realism-full`, 10,000 profiles, checksum recorded in
`docs/v0.4.0/dataset-v2-full-audit.md`
**Status:** source semantics verified; field-level 10K prevalence is not
recomputed because the generated full corpus is not present in this checkout.

This audit does not mutate Dataset v2, generate a replacement corpus, or infer
values from search text. The full-corpus quality figures below are carried
forward from the completed Gate 5.5B audit; `not independently measurable`
means that a raw 10K artifact is required before assigning a null rate.

## Evidence and semantics

| Semantic | Source truth and definition | 10K evidence available here | Completeness status | Unknown/open semantics |
|---|---|---:|---|---|
| `years_experience` | `V2ExpertProfile.years_experience`: generated total career experience, integer 0–80; it is not domain-specific experience. | not independently measurable | NOT_READY | missing/unknown must exclude a hard constraint; no imputation |
| `seniority` | `V2ExpertProfile.seniority`: closed enum `mid`, `senior`, `principal`. Source supports the ordering `mid < senior < principal`; no other levels are implied. | not independently measurable; schema enum verified | READY_WITH_LIMITATIONS | ordering is valid only for this enum; missing is unknown |
| `industry` | profile `industries` plus employment/project `industry`; provenance matters. | not independently measurable | READY_WITH_LIMITATIONS | profile aggregate must not be confused with a specific project/employment industry |
| `role` | profile `roles` plus employment/project `role`; relationship-specific role is distinct from aggregate role. | not independently measurable | READY_WITH_LIMITATIONS | a profile-level role cannot prove role during a requested interval |
| employment interval | `V2Employment.start_date` required, `end_date` nullable; `end_date=null` means current/open-ended only when `current=true`, otherwise unknown requires validation. | prior audit: invalid temporal records 0 | READY_WITH_LIMITATIONS | open-ended and unknown must remain distinct |
| project interval | `V2Project.start_date` and `end_date` required. | prior audit: invalid temporal records 0 | READY_WITH_LIMITATIONS | closed interval; no inferred continuation |
| relationship interval | `V2Relationship.valid_from/valid_to` nullable and evidence-backed. | prior audit: invalid temporal records 0 | READY_WITH_LIMITATIONS | null interval means unspecified, not an all-time assertion |
| employer organization | `V2Employment.organization_id/name`; typed employment relationship. | not independently measurable | READY_WITH_LIMITATIONS | keep separate from client/project organization |
| project client | `V2Project.client_id/name`; typed project client relationship. | not independently measurable | READY_WITH_LIMITATIONS | must not satisfy an employer constraint |
| relationship | `V2Relationship` predicate, object id/type, optional interval and evidence ids. | prior audit: relationship model and evidence coverage verified | READY_WITH_LIMITATIONS | nested relation is required to prevent cross-object matches |
| delivery/advisory | `V2Project.delivery_level` (`hands_on`, `technical_lead`, `advisory`) plus evidence kind (`hands_on_delivery`, `leadership`, `advisory_exposure`). | prior audit: evidence coverage 100% for positive judgements | READY_WITH_LIMITATIONS | delivery level and evidence kind must remain separate |

## Carried-forward full-corpus facts

- 10,000 profiles, 120 queries and 1,200,000 judgements were generated with
  deterministic manifest/checksum controls.
- Invalid temporal records: 0 in the completed Gate 5.5B audit.
- The corpus remains a controlled synthetic relevance benchmark; templated
  language and controlled-vocabulary leakage risk limit generalization.
- Gold is an independent structured audit, not external human ground truth.

The following prevalence values are intentionally **not invented** in this
checkout: present/missing counts, null rates, industry normalization counts,
role multiplicity, organization/client counts, and relationship interval
coverage. A future evidence package must include the raw corpus or a signed
field-profile report before those values can be used to approve a compiler.

## Stop-condition assessment

Gate 1.5 does not approve Gate 2 runtime compilation yet. A useful bounded
subset remains possible after the versioned projection is built: categorical
profile fields and explicitly scoped nested relationship predicates. Numeric
experience, temporal intervals, delivery/advisory evidence, and all
relationship-with-object operations remain restricted until projection-level
completeness evidence is available.
