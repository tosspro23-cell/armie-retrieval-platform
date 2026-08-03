"""Versioned Elasticsearch mapping for ExpertProfile projections."""

from __future__ import annotations


MAPPING_VERSION = "expert-discovery-es-mapping-v1"


def build_index_name(build_id: str) -> str:
    if not build_id or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in build_id):
        raise ValueError("build_id must be a safe non-empty identifier")
    return f"armie-experts-v1-{build_id}"


def build_mapping(*, embedding_dimensions: int = 768, embedding_model: str = "BAAI/bge-m3") -> dict:
    return {
        "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}, "similarity": {"default": {"type": "BM25", "k1": 1.2, "b": 0.75}}},
        "mappings": {
            "dynamic": "strict",
            "_meta": {"mapping_version": MAPPING_VERSION, "embedding_model": embedding_model, "embedding_dimensions": embedding_dimensions},
            "properties": {
                "expert_id": {"type": "keyword"}, "display_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "headline": {"type": "text"}, "summary": {"type": "text"},
                "skills": {"type": "keyword"}, "industries": {"type": "keyword"}, "technologies": {"type": "keyword"},
                "roles": {"type": "keyword"}, "locations": {"type": "keyword"},
                "project_titles": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "project_descriptions": {"type": "text"}, "project_industries": {"type": "keyword"},
                "employer_names": {"type": "keyword"}, "employer_descriptions": {"type": "text"},
                "delivery_evidence": {"type": "keyword"},
                "embedding": {"type": "dense_vector", "dims": embedding_dimensions, "index": False, "similarity": "dot_product"},
            },
        },
    }
