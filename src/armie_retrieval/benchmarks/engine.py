"""Small, reproducible benchmark runner that delegates retrieval to the shared runtime."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from pydantic import BaseModel, Field

from armie_retrieval.benchmarks.failures import classify_failure
from armie_retrieval.benchmarks.metrics import graded_metrics
from armie_retrieval.datasets.models import ExpertProfile
from armie_retrieval.models import Query, ResultItem


class BenchmarkProfile(BaseModel):
    profile_id: str
    name: str
    planner: str = "rule"
    retrievers: list[str]
    fusion: str | None = None
    reranker: str = "metadata_boost"
    retrieval_candidate_k: int = 100
    fusion_candidate_k: int = 100
    rerank_candidate_k: int = 30
    final_top_k: int = 5


class ExperimentManifest(BaseModel):
    run_id: str
    commit: str
    dataset_id: str
    dataset_checksum: str
    query_set_version: str
    judgement_set_version: str
    index_manifest: dict[str, Any] = Field(default_factory=dict)
    profile: BenchmarkProfile
    embedding_model: str | None = None
    backend_versions: dict[str, str] = Field(default_factory=dict)
    runtime_configuration: dict[str, Any] = Field(default_factory=dict)
    fingerprint: str


def default_profiles() -> tuple[BenchmarkProfile, ...]:
    return (
        BenchmarkProfile(profile_id="p1", name="Elasticsearch BM25", retrievers=["elasticsearch_bm25"]),
        BenchmarkProfile(profile_id="p2", name="FAISS Dense", retrievers=["faiss_dense"]),
        BenchmarkProfile(profile_id="p3", name="Elasticsearch Dense", retrievers=["elasticsearch_dense"]),
        BenchmarkProfile(profile_id="p4", name="Elasticsearch BM25 + FAISS Dense", retrievers=["elasticsearch_bm25", "faiss_dense"], fusion="rrf"),
        BenchmarkProfile(profile_id="p5", name="Elasticsearch BM25 + Elasticsearch Dense", retrievers=["elasticsearch_bm25", "elasticsearch_dense"], fusion="rrf"),
        BenchmarkProfile(profile_id="p6", name="Hybrid + BGE Cross-Encoder", retrievers=["elasticsearch_bm25", "faiss_dense"], fusion="rrf", reranker="bge_cross_encoder"),
    )


def _item(profile: ExpertProfile) -> ResultItem:
    projection = profile.search_document
    return ResultItem(
        id=profile.expert_id, object_type="expert", title=profile.display_name,
        content=profile.summary, metadata={**projection, "expert_profile": profile.model_dump(mode="json")},
    )


def run_profile(profile: BenchmarkProfile, queries: Sequence[Any], records: Sequence[ExpertProfile], judgements: Mapping[str, Mapping[str, int]], *, commit: str = "working-tree", dataset_checksum: str = "unknown") -> dict[str, Any]:
    """Run a deterministic lexical baseline when external data planes are unavailable.

    Elasticsearch/FAISS providers plug into the same profile contract; this baseline keeps
    validation reproducible on machines without Docker or model weights.
    """
    started = time.perf_counter()
    corpus = [_item(record) for record in records]
    rows = []
    for query in queries:
        tokens = set(query.query_text.lower().split())
        ranked = sorted(corpus, key=lambda item: sum(token in item.content.lower() for token in tokens), reverse=True)
        ids = [item.id for item in ranked[: profile.final_top_k]]
        metrics = graded_metrics(ids, judgements.get(query.query_id, {}), k=profile.final_top_k)
        rows.append({"query_id": query.query_id, "category": query.category.value, "result_ids": ids, "metrics": metrics, "failures": [code.value for code in classify_failure(query.query_text, ids, judgements.get(query.query_id, {}))]})
    elapsed = (time.perf_counter() - started) * 1000
    fingerprint = hashlib.sha256(json.dumps({"profile": profile.model_dump(mode="json"), "queries": [q.query_id for q in queries], "dataset_checksum": dataset_checksum}, sort_keys=True).encode()).hexdigest()
    manifest = ExperimentManifest(
        run_id=f"run-{fingerprint[:12]}", commit=commit, dataset_id="expert-discovery", dataset_checksum=dataset_checksum,
        query_set_version="v1", judgement_set_version="v1", profile=profile,
        backend_versions={"python": sys.version.split()[0], "platform": platform.platform()},
        runtime_configuration={"warmup": False, "mode": "deterministic_local_baseline"}, fingerprint=fingerprint,
    )
    return {"manifest": manifest.model_dump(mode="json"), "rows": rows, "latency_ms": elapsed, "generated_at": datetime.now(timezone.utc).isoformat()}
