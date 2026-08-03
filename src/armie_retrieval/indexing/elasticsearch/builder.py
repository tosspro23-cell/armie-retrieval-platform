"""Offline Elasticsearch index construction; online retrievers only consume artifacts."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from armie_retrieval.datasets.models import ExpertProfile
from armie_retrieval.embeddings import EmbeddingProvider
from armie_retrieval.indexing.serializers import searchable_text
from armie_retrieval.models import ResultItem

from .client import ElasticsearchClient
from .mapping import build_index_name, build_mapping


class ElasticsearchIndexBuilder:
    def __init__(self, client: ElasticsearchClient, embedding_provider: EmbeddingProvider | None = None) -> None:
        self.client = client
        self.embedding_provider = embedding_provider

    def build(self, profiles: Iterable[ExpertProfile], *, build_id: str, embedding_model: str = "BAAI/bge-m3") -> dict:
        records = list(profiles)
        index = build_index_name(build_id)
        dimensions = 768
        vectors: list[list[float]] = []
        if self.embedding_provider is not None:
            # Keep the Elasticsearch dense projection identical to the FAISS
            # offline projection so Gate 3 compares the same model/input
            # representation rather than two different text views.
            embedding_texts = [
                searchable_text(ResultItem(
                    id=profile.expert_id,
                    object_type="expert",
                    title=profile.display_name,
                    content=profile.summary,
                    metadata=profile.search_document,
                ))
                for profile in records
            ]
            vectors = self.embedding_provider.embed(embedding_texts)
            dimensions = len(vectors[0]) if vectors else dimensions
        self.client.create_index(index, build_mapping(embedding_dimensions=dimensions, embedding_model=embedding_model))
        documents = []
        for position, profile in enumerate(records):
            document = dict(profile.search_document)
            if vectors:
                document["embedding"] = vectors[position]
            documents.append(document)
        outcome = self.client.bulk_index(index, documents)
        manifest = {
            "index": index,
            "mapping_version": "expert-discovery-es-mapping-v1",
            "document_count": len(records),
            "embedding_model": embedding_model,
            "embedding_dimensions": dimensions,
            "dataset_checksum": hashlib.sha256(json.dumps([record.expert_id for record in records], sort_keys=True).encode()).hexdigest(),
            "outcome": outcome,
        }
        self.client.alias("armie-experts-read", index)
        self.client.alias("armie-experts-write", index, write=True)
        return manifest
