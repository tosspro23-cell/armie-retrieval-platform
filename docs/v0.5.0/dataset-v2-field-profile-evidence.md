# Dataset v2 field-profile evidence package

**Gate:** 2A
**Run identity:** deterministic reproduction, seed `7301`, query seed `9137`
**Dataset:** `v2-realism-full`, 10,000 profiles, checksum
`514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc`
**Generator:** `expert-discovery-generator-v2-realism-0.2-r2`
**Source:** `V2ExpertProfile` records; no free-text inference.

## Profile fields

| Field | Present | Missing/null | Summary |
|---|---:|---:|---|
| years_experience | 10,000 | 0 | min 5, max 25, mean 12.845, median 9; buckets 0–9: 6,155; 10–19: 1,538; 20–29: 2,307 |
| seniority | 10,000 | 0 | mid 2,308; senior 3,847; principal 3,845 |
| industries | 10,000 | 0 | one profile value each in this generator; canonical values retained |
| roles | 10,000 | 0 | one profile value each; employment/project roles remain separate |
| locations | 10,000 | 0 | one profile value each; normalization is generator-controlled |

`years_experience` is total career experience under the source generator
contract (integer range 0–80); the reproduced corpus happens to range 5–25.
`seniority` is the closed enum `mid`, `senior`, `principal`, with deterministic
rank `1`, `2`, `3` respectively. This ordering is not generalized beyond the
enum.

## Employment and projects

- Employment records: 10,000 (one per profile); organization, role, industry
  and start date are present in all records.
- Employment end dates: 8,571 closed; 1,429 open-ended with
  `end_date=null AND current=true`; no unknown combination observed.
- Projects: 10,000 (one per profile); client, role, industry and start/end are
  present in all records.
- Delivery levels: `hands_on` 7,500; `technical_lead` 2,500; `advisory` 0 in
  this reproduced full corpus.

## Relationships and evidence

- Relationships: 53,334. Predicates: works_at 10,000, delivered_for 10,000,
  has_project 10,000, in_industry 10,000, located_in 10,000, advised 3,334.
- Relationship object types: employer 10,000; client 13,334; project 10,000;
  industry 10,000; location 10,000.
- All 53,334 relationships have evidence IDs; 33,334 have `valid_from` and
  31,905 have `valid_to`.
- Evidence records: 33,334, all with structured provenance and object linkage.
  Kinds: employer_relationship 10,000; hands_on_delivery 10,000;
  skill_mention 10,000; advisory_exposure 3,334.

## Projection implications

The evidence supports a deterministic useful subset: profile categorical
fields and explicitly scoped seniority rank, plus nested structures for
employment, projects, relationships and evidence. Temporal overlap and
relationship object compilation remain deferred until Gate 2 semantics and
nested mapping tests are approved. The source `works_at` predicate is
normalized to the contract vocabulary `worked_at` only in the projection; no
source record is mutated.

This is a controlled synthetic relevance benchmark. It is not external human
ground truth and must not be generalized to natural expert-network data.
