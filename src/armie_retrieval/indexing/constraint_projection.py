"""Deterministic, backend-neutral v0.5 constraint projection."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

PROJECTION_SCHEMA_VERSION = "armie-v0.5-constraint-projection-v1"
PROJECTION_IMPLEMENTATION_VERSION = "constraint-projection-0.2-gate6b"
SENIORITY_RANK = {"mid": 1, "senior": 2, "principal": 3}


def _date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def project_profile(profile: Any) -> dict[str, Any]:
    """Project canonical V2 profile truth without text-derived fallbacks."""
    return {
        "expert_id": profile.expert_id,
        "years_experience": profile.years_experience,
        "industries": list(profile.industries),
        "roles": list(profile.roles),
        "seniority": profile.seniority,
        "seniority_rank": SENIORITY_RANK[profile.seniority],
        "locations": list(profile.locations),
        "employments": [{"organization_id": e.organization_id, "organization_name": e.organization_name, "role": e.role, "industry": e.industry, "start_date": _date(e.start_date), "end_date": _date(e.end_date), "current": e.current, "evidence_ids": list(e.evidence_ids)} for e in profile.employers],
        "projects": [{"client_id": p.client_id, "client_name": p.client_name, "role": p.role, "industry": p.industry, "start_date": _date(p.start_date), "end_date": _date(p.end_date), "delivery_level": p.delivery_level, "concepts": list(p.canonical_concepts), "evidence_ids": list(p.evidence_ids)} for p in profile.projects],
        "relationships": [{"predicate": "worked_at" if r.predicate == "works_at" else r.predicate, "object_id": r.object_id, "object_type": r.object_type, "valid_from": _date(r.valid_from), "valid_to": _date(r.valid_to), "evidence_ids": list(r.evidence_ids)} for r in profile.relationships],
        "evidence": [{"evidence_kind": e.evidence_kind, "source_id": e.source_id, "object_id": e.object_id, "subject_id": e.subject_id, "provenance_kind": e.provenance_kind} for e in profile.evidence],
    }


def projection_mapping() -> dict[str, Any]:
    nested = {"type": "nested", "properties": {"organization_id": {"type": "keyword"}, "organization_name": {"type": "keyword"}, "client_id": {"type": "keyword"}, "client_name": {"type": "keyword"}, "role": {"type": "keyword"}, "industry": {"type": "keyword"}, "start_date": {"type": "date"}, "end_date": {"type": "date"}, "current": {"type": "boolean"}, "delivery_level": {"type": "keyword"}, "concepts": {"type": "keyword"}, "evidence_ids": {"type": "keyword"}}}
    relation = {"type": "nested", "properties": {"predicate": {"type": "keyword"}, "object_id": {"type": "keyword"}, "object_type": {"type": "keyword"}, "valid_from": {"type": "date"}, "valid_to": {"type": "date"}, "evidence_ids": {"type": "keyword"}}}
    evidence = {"type": "nested", "properties": {"evidence_kind": {"type": "keyword"}, "source_id": {"type": "keyword"}, "object_id": {"type": "keyword"}, "subject_id": {"type": "keyword"}, "provenance_kind": {"type": "keyword"}}}
    return {"settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}}, "mappings": {"dynamic": "strict", "_meta": {"projection_schema_version": PROJECTION_SCHEMA_VERSION, "embedding_model": "BAAI/bge-m3", "embedding_dimensions": 1024}, "properties": {"expert_id": {"type": "keyword"}, "years_experience": {"type": "integer"}, "industries": {"type": "keyword"}, "roles": {"type": "keyword"}, "seniority": {"type": "keyword"}, "seniority_rank": {"type": "integer"}, "locations": {"type": "keyword"}, "employments": nested, "projects": nested, "relationships": relation, "evidence": evidence, "embedding": {"type": "dense_vector", "dims": 1024, "index": True, "similarity": "dot_product"}}}}


def projection_manifest(dataset_checksum: str, record_count: int, source_generator_version: str) -> dict[str, Any]:
    mapping_fingerprint = hashlib.sha256(json.dumps(projection_mapping(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"dataset_checksum": dataset_checksum, "projection_schema_version": PROJECTION_SCHEMA_VERSION, "projection_implementation_version": PROJECTION_IMPLEMENTATION_VERSION, "source_generator_version": source_generator_version, "record_count": record_count, "mapping_fingerprint": mapping_fingerprint, "build_identity": "deterministic"}
