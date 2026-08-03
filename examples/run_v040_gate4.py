"""Run the real v0.4.0 Gate 4 H1-H4 profiles through ARMIE runtime.

This script intentionally requires a running pinned Elasticsearch instance and
locally cached BGE models. It never substitutes a mock backend or silently
falls back when a required profile component is unavailable.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from armie_retrieval.embeddings import BGEEmbeddingProvider
from armie_retrieval.models import Query
from armie_retrieval.observability import trace_query
from armie_retrieval.planners import RuleBasedPlanner
from armie_retrieval.processors import DeduplicateProcessor, QueryAwareRerankProcessor
from armie_retrieval.indexing.elasticsearch import ElasticsearchClient
from armie_retrieval.providers.elasticsearch import (
    ElasticsearchBM25Retriever,
    ElasticsearchDenseRetriever,
    ElasticsearchHybridRetriever,
)
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry
from armie_retrieval.rerankers import BGECrossEncoderReranker, MetadataBoostReranker
from armie_retrieval.runtime import RetrievalRuntime


BOUNDARIES = {
    "retrieval_candidate_k": 100,
    "fusion_candidate_k": 100,
    "rerank_candidate_k": 30,
    "final_top_k": 5,
    "rrf_k": 60,
}

QUERIES = (
    ("exact_skill", "Find experts with Elasticsearch experience"),
    ("skill_industry", "Find healthcare experts with Azure AI experience"),
    ("delivery_project", "Find people who delivered a production RAG platform"),
    ("organization", "Find experts who worked at Northstar Health"),
    ("semantic_paraphrase", "Locate practitioners who built meaning-aware search"),
    ("multi_constraint", "Find senior Portugal experts in energy using FAISS"),
    ("hard_negative", "Find delivery leaders who implemented Elasticsearch"),
)


def _runtime(index: str, reranker) -> tuple[RetrievalRuntime, RetrieverRegistry, QueryAwareRerankProcessor]:
    client = ElasticsearchClient(timeout=60)
    dense = ElasticsearchDenseRetriever(client, index=index, embedding_provider=EMBEDDING)
    sparse = ElasticsearchBM25Retriever(client, index=index)
    hybrid = ElasticsearchHybridRetriever(dense, sparse, rrf_k=int(BOUNDARIES["rrf_k"]))
    retrievers = RetrieverRegistry()
    retrievers.register("elasticsearch_bm25", sparse, capabilities={"sparse"}, version="8.15.3", priority=100)
    retrievers.register("elasticsearch_dense", dense, capabilities={"dense"}, version="8.15.3", priority=100)
    retrievers.register("elasticsearch_hybrid", hybrid, capabilities={"hybrid"}, version="8.15.3", priority=100)
    processors = ProcessorRegistry()
    processors.register("deduplicate", DeduplicateProcessor(), capabilities={"deduplicate"}, version="0.4.0", priority=100)
    rerank_processor = QueryAwareRerankProcessor(reranker, name="rerank")
    processors.register("rerank", rerank_processor, capabilities={"rerank"}, version="0.4.0", priority=100)
    return RetrievalRuntime(retrievers, processors), retrievers, rerank_processor


def _profile(profile_id: str, index: str, *, bge: bool) -> dict:
    strategy = {"H1": "sparse", "H2": "dense", "H3": "hybrid", "H4": "hybrid"}[profile_id]
    reranker = BGECrossEncoderReranker(isolated=False) if bge else MetadataBoostReranker()
    if bge:
        reranker.validate_model_available()
    runtime, retrievers, processor = _runtime(index, reranker)
    planner = RuleBasedPlanner(
        retrievers.capabilities(),
        strategy_override=strategy,
        processor_names=("deduplicate", "rerank"),
        parameters=BOUNDARIES,
    )
    processor.selection = type("Selection", (), {
        "requested": "bge_cross_encoder" if bge else "metadata_boost",
        "actual": "bge_cross_encoder" if bge else "metadata_boost",
        "requested_model": getattr(reranker, "model_name", None),
        "fallback_reason": None,
    })()
    rows = []
    for category, text in QUERIES:
        query = Query(text=text, top_k=int(BOUNDARIES["final_top_k"]), request_id=f"gate4-{profile_id}-{category}")
        started = time.perf_counter()
        result, trace = trace_query(runtime, planner, query, query_id=query.request_id)
        payload = trace.to_dict()
        payload["profile_id"] = profile_id
        payload["category"] = category
        payload["query_text"] = text
        payload["runtime_elapsed_ms"] = (time.perf_counter() - started) * 1000
        payload["top_k_ids"] = [item.id for item in result.items]
        payload["candidate_boundaries"] = dict(BOUNDARIES)
        rows.append(payload)
    return {"profile_id": profile_id, "reranker": getattr(reranker, "name", type(reranker).__name__), "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="armie-experts-v1-gate23b-20260803")
    parser.add_argument("--output", type=Path, default=Path("/tmp/armie-v040-gate4.json"))
    args = parser.parse_args()
    global EMBEDDING
    EMBEDDING = BGEEmbeddingProvider()
    EMBEDDING.validate_model_available()
    health = ElasticsearchClient(timeout=10).health()
    if health["version"] != "8.15.3" or health["cluster"]["status"] != "green":
        raise RuntimeError(f"Gate 4 requires Elasticsearch 8.15.3 green cluster: {health}")
    output = {
        "elasticsearch": health,
        "embedding_model": EMBEDDING.model_name,
        "candidate_boundaries": BOUNDARIES,
        "profiles": [_profile("H1", args.index, bge=False), _profile("H2", args.index, bge=False), _profile("H3", args.index, bge=False), _profile("H4", args.index, bge=True)],
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "profiles": [p["profile_id"] for p in output["profiles"]], "queries_per_profile": len(QUERIES)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
