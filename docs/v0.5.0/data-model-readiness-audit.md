# v0.5.0 Data-model readiness audit

**Status:** Gate 1.5 read-only audit; no Dataset v2 mutation and no
Elasticsearch changes.
**Sources:** Dataset v2 Pydantic models/generator, completed v0.4.0 Gate 5.5B
full-corpus audit, v0.4.0 mapping and dataset design documents. The raw 10K
generated artifact is not present in this checkout, so prevalence/null rates
are not fabricated. See [the completeness audit](dataset-v2-constraint-completeness-audit.md).

## Classification summary

| Candidate field/semantic | Canonical source | Type | Current projection/mapping | Status | Limitation |
|---|---|---|---|---|---|
| `years_experience` | `V2ExpertProfile.years_experience` | integer | absent from v0.4 projection | NOT_READY | Total career experience is defined in source, but 10K prevalence and v0.5 projection evidence are absent. |
| `industry` | profile/employment/project industry | keyword + nested provenance | flattened/partial | READY_WITH_LIMITATIONS | Profile aggregate cannot prove project/employment context. |
| `location` | `V2ExpertProfile.locations` | keyword[] | keyword concept exists | READY_WITH_LIMITATIONS | Normalization and prevalence not independently measured. |
| `role` | profile/employment/project role | keyword + nested provenance | flattened/partial | READY_WITH_LIMITATIONS | Profile role cannot prove role during an interval. |
| `seniority` | closed enum mid/senior/principal | keyword + explicit rank | absent from v0.4 projection | READY_WITH_LIMITATIONS | Ordering is justified only for the closed source enum; projection pending. |
| temporal dates | employment/project/relationship intervals | nested date intervals | absent/flattened in v0.4 | READY_WITH_LIMITATIONS | Open-ended, unknown and overlap semantics require v0.5 projection. |
| prohibited capability | canonical concepts + evidence/advisory signals | nested evidence | no authoritative exclusion field | DEFERRED | Requires explicit evidence-aware negative projection. |
| organization/employer/client | typed employment and project client IDs | nested typed objects | flattened keyword fields | READY_WITH_LIMITATIONS | Employer and client must remain separate nested relations. |
| relationship representation | predicate/object/interval/evidence | nested typed edges | predicate-only mapping | READY_WITH_LIMITATIONS | Flat fields would create cross-object false matches. |
| delivery/advisory semantics | project delivery level + evidence kind | nested project/evidence | partial fields | READY_WITH_LIMITATIONS | Advisory is not equivalent to hands-on delivery. |

## Findings

The contract layer can represent more semantics than the current Dataset v2
projection and index can enforce. Numeric experience is **NOT_READY**. Profile
industry, location, role, seniority, organization/client and relationship
presence are **READY_WITH_LIMITATIONS**, not proof of safe hard filtering.
Temporal, relationship and evidence semantics require nested projection before
compilation. Prohibited capability is **DEFERRED** rather than inferred from
search text.

The source models preserve typed employment, project, relationship and evidence
records. The current Elasticsearch mapping is a flattened v0.4 artifact and
does not contain every source field. No exact null/missing prevalence is
claimed here; those values are `TBD — requires benchmark-data audit`.

## Gate 2 blockers

Before compiling filters, a later gate must approve the versioned projection in
`constraint-projection-design.md`, attach field-level prevalence evidence from
the 10K artifact, and define unknown behavior from canonical data rather than
search text.
