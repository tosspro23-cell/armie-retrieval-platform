"""Build an isolated Gate 6B dense index with canonical constraint fields."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from armie_retrieval.datasets.v2 import V2ExpertProfile
from armie_retrieval.indexing.constraint_projection import (
    PROJECTION_IMPLEMENTATION_VERSION,
    PROJECTION_SCHEMA_VERSION,
    project_profile,
)
from armie_retrieval.indexing.elasticsearch import ElasticsearchClient


def mapping_from(source_mapping: dict) -> dict:
    mapping = json.loads(json.dumps(source_mapping))
    mapping.setdefault("settings", {}).setdefault("index", {})["number_of_replicas"] = 0
    properties = mapping["mappings"]["properties"]
    properties.update({"years_experience": {"type": "integer"}, "seniority": {"type": "keyword"}, "seniority_rank": {"type": "integer"}})
    mapping["mappings"].setdefault("_meta", {})
    mapping["mappings"]["_meta"].update({"mapping_version": "expert-discovery-es-mapping-v2-gate6b", "projection_schema_version": PROJECTION_SCHEMA_VERSION, "projection_implementation_version": PROJECTION_IMPLEMENTATION_VERSION, "embedding_model": "BAAI/bge-m3", "embedding_dimensions": 1024})
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--source-index", required=True)
    parser.add_argument("--target-index", required=True)
    parser.add_argument("--dataset-checksum", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    client = ElasticsearchClient(timeout=120)
    source_mapping = client.request("GET", f"{args.source_index}/_mapping").json()[args.source_index]
    source = client.request("POST", f"{args.source_index}/_search", json={"size": 10000, "query": {"match_all": {}}}).json()
    hits = source.get("hits", {}).get("hits", [])
    if len(hits) != 10000:
        raise RuntimeError(f"expected 10000 source documents, got {len(hits)}")
    profiles = [V2ExpertProfile.model_validate(row) for row in json.loads(args.canonical.read_text())]
    if len(profiles) != 10000:
        raise RuntimeError(f"expected 10000 canonical profiles, got {len(profiles)}")
    by_id = {profile.expert_id: project_profile(profile) for profile in profiles}
    if set(by_id) != {str(hit["_id"]) for hit in hits}:
        raise RuntimeError("canonical and source index identity sets differ")
    mapping = mapping_from(source_mapping)
    mapping_fingerprint = hashlib.sha256(json.dumps(mapping, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    client.create_index(args.target_index, mapping)
    documents = []
    for hit in hits:
        expert_id = str(hit["_id"])
        document = dict(hit.get("_source", {}))
        canonical = by_id[expert_id]
        for field in ("years_experience", "seniority", "seniority_rank", "industries", "roles", "locations"):
            document[field] = canonical[field]
        documents.append(document)
    outcome = client.bulk_index(args.target_index, documents, batch_size=250)
    client.request("POST", f"{args.target_index}/_refresh")
    count = client.request("GET", f"{args.target_index}/_count").json()["count"]
    if outcome.get("rejected", 0) or count != 10000:
        raise RuntimeError(f"index build failed: {outcome}, count={count}")
    result = {"index": args.target_index, "source_index": args.source_index, "document_count": count, "dataset_checksum": args.dataset_checksum, "projection_schema_version": PROJECTION_SCHEMA_VERSION, "projection_implementation_version": PROJECTION_IMPLEMENTATION_VERSION, "mapping_fingerprint": mapping_fingerprint, "embedding_model": "BAAI/bge-m3", "embedding_dimensions": 1024, "bulk_outcome": outcome}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
