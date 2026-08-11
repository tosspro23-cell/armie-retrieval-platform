"""Offline Elasticsearch index construction; online retrievers only consume artifacts."""

from __future__ import annotations

import hashlib
import json
import platform
import resource
import time
from pathlib import Path
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

    def build(self, profiles: Iterable[ExpertProfile], *, build_id: str, embedding_model: str = "BAAI/bge-m3", batch_size: int = 16, checkpoint_path: str | Path | None = None, embedding_artifact: str | Path | None = None) -> dict:
        records = list(profiles)
        index = build_index_name(build_id)
        dimensions = int(getattr(self.embedding_provider, "dimension", 1024)) if self.embedding_provider is not None else 768
        checkpoint_file = Path(checkpoint_path) if checkpoint_path else None
        artifact_file = Path(embedding_artifact) if embedding_artifact else None
        completed_ids: set[str] = set()
        if checkpoint_file and checkpoint_file.exists():
            checkpoint = json.loads(checkpoint_file.read_text())
            expected = {"dataset_checksum": hashlib.sha256(json.dumps([record.expert_id for record in records], sort_keys=True).encode()).hexdigest(), "embedding_model": embedding_model, "embedding_dimensions": dimensions, "target_index": index}
            if any(checkpoint.get(k) != v for k, v in expected.items()):
                raise ValueError("dense-index checkpoint identity mismatch; refusing resume")
            completed_ids = set(checkpoint.get("completed_ids", []))
        if self.embedding_provider is not None:
            dimensions = int(getattr(self.embedding_provider, "dimension", dimensions))
        if not completed_ids:
            self.client.create_index(index, build_mapping(embedding_dimensions=dimensions, embedding_model=embedding_model))
        indexed = 0; failures = 0; started = time.perf_counter(); persisted = 0; vectors_produced = 0
        device = str(getattr(getattr(self.embedding_provider, "_model", None), "device", "unknown")) if self.embedding_provider is not None else "none"

        def rss_mb() -> float:
            value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # macOS reports bytes; Linux reports KiB.
            return value / (1024 * 1024) if platform.system() == "Darwin" else value / 1024

        for offset in range(0, len(records), max(1, batch_size)):
            batch = [p for p in records[offset:offset + max(1, batch_size)] if p.expert_id not in completed_ids]
            if not batch: continue
            vectors = self.embedding_provider.embed([searchable_text(ResultItem(id=p.expert_id, object_type="expert", title=p.display_name, content=p.summary, metadata=p.search_document)) for p in batch]) if self.embedding_provider is not None else [None] * len(batch)
            vectors_produced += len(vectors)
            documents = []
            for profile, vector in zip(batch, vectors):
                document = dict(profile.search_document)
                if vector is not None: document["embedding"] = vector
                documents.append(document)
            outcome = self.client.bulk_index(index, documents); indexed += outcome.get("indexed", 0); failures += outcome.get("rejected", 0)
            if artifact_file and vectors and self.embedding_provider is not None:
                artifact_file.parent.mkdir(parents=True, exist_ok=True)
                with artifact_file.open("a", encoding="utf-8") as handle:
                    for profile, vector in zip(batch, vectors): handle.write(json.dumps({"expert_id": profile.expert_id, "vector": vector}) + "\n")
                persisted += len(vectors)
            completed_ids.update(p.expert_id for p in batch)
            if checkpoint_file:
                checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_file.write_text(json.dumps({"dataset_checksum": hashlib.sha256(json.dumps([record.expert_id for record in records], sort_keys=True).encode()).hexdigest(), "dataset_version": "v2-realism-full", "embedding_model": embedding_model, "embedding_dimensions": dimensions, "target_index": index, "completed_ids": sorted(completed_ids), "processed": len(completed_ids), "vectors_persisted": persisted, "batch_size": batch_size}, indent=2))
            print(json.dumps({"processed": len(completed_ids), "batch_size": batch_size, "rss_mb": round(rss_mb(), 1), "device": device, "elapsed_s": round(time.perf_counter() - started, 2), "indexed": indexed, "bulk_successes": indexed, "bulk_failures": failures, "vectors_produced": vectors_produced, "vectors_persisted": persisted}), flush=True)
        outcome = {"indexed": indexed, "rejected": failures, "index": index}
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
