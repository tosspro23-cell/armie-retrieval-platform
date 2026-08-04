"""Provider implementations that consume Elasticsearch indexes at query time."""

from __future__ import annotations

import time
from typing import Any

from armie_retrieval.indexing.elasticsearch.client import ElasticsearchClient
from armie_retrieval.models import Query, ResultItem, RetrievalPlan, RetrievalResult


class _BaseElasticsearchRetriever:
    capabilities = frozenset({"elasticsearch", "metadata_filter"})

    def __init__(self, client: ElasticsearchClient, *, index: str) -> None:
        self.client = client
        self.index = index

    def _result(self, query: Query, plan: RetrievalPlan, hits: list[dict[str, Any]], started: float, score_type: str) -> RetrievalResult:
        items = tuple(ResultItem(
            id=str(hit.get("_id")), object_type="expert", title=hit.get("_source", {}).get("display_name", str(hit.get("_id"))),
            content=hit.get("_source", {}).get("summary", ""), metadata=hit.get("_source", {}), score=float(hit.get("_score") or 0.0),
            signals={score_type: float(hit.get("_score") or 0.0)}, sources=(self.name,),
        ) for hit in hits)
        return RetrievalResult(items=items, plan_id=plan.plan_id, strategy=plan.strategy, latency_ms=(time.perf_counter() - started) * 1000,
                               provenance={"retrievers": [self.name], "provider": self.name, "index": self.index, "score_type": score_type}, trace=(f"retrieved:{self.name}",))


class ElasticsearchBM25Retriever(_BaseElasticsearchRetriever):
    name = "elasticsearch_bm25"
    capabilities = frozenset({"sparse", "elasticsearch", "bm25", "metadata_filter"})

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        should = [{"match": {field: {"query": query.text, "boost": boost}}} for field, boost in (
            ("skills", 4.0), ("technologies", 4.0), ("project_titles", 3.0), ("project_descriptions", 2.5),
            ("industries", 2.0), ("roles", 2.0), ("headline", 1.5), ("summary", 1.0),
        )]
        filters = [{"term": {key: value}} for key, value in query.filters.items()]
        payload = {"size": int(plan.parameters.get("retrieval_candidate_k", plan.top_k)), "query": {"bool": {"should": should, "minimum_should_match": 1, "filter": filters}}}
        hits = self.client.request("POST", f"{self.index}/_search", json=payload).json().get("hits", {}).get("hits", [])
        return self._result(query, plan, hits, started, "bm25_score")


class ElasticsearchDenseRetriever(_BaseElasticsearchRetriever):
    name = "elasticsearch_dense"
    capabilities = frozenset({"dense", "elasticsearch", "knn"})

    def __init__(self, client: ElasticsearchClient, *, index: str, embedding_provider) -> None:
        super().__init__(client, index=index)
        self.embedding_provider = embedding_provider

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        vector = self.embedding_provider.embed([query.text])[0]
        candidate_k = int(plan.parameters.get("retrieval_candidate_k", plan.top_k))
        payload = {
            "size": candidate_k,
            "knn": {
                "field": "embedding",
                "query_vector": vector,
                "k": candidate_k,
                "num_candidates": candidate_k * 2,
            },
        }
        hits = self.client.request("POST", f"{self.index}/_search", json=payload).json().get("hits", {}).get("hits", [])
        return self._result(query, plan, hits, started, "elasticsearch_dense_score")


class ElasticsearchHybridRetriever:
    """Real Elasticsearch BM25+dense retrieval with ARMIE RRF semantics.

    The component is registered as one runtime capability, while retaining
    both child providers so the shared trace collector can expose every source
    contribution and rank. Raw BM25 and dense scores are never normalized or
    compared; only source ranks participate in RRF.
    """

    name = "elasticsearch_hybrid"
    capabilities = frozenset({"hybrid", "elasticsearch", "rrf"})

    def __init__(self, dense: ElasticsearchDenseRetriever, sparse: ElasticsearchBM25Retriever, *, rrf_k: int = 60) -> None:
        self._dense = dense
        self._sparse = sparse
        self._rrf_k = rrf_k

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        dense_result = self._dense.retrieve(query, plan)
        sparse_result = self._sparse.retrieve(query, plan)
        fusion_started = time.perf_counter()
        scores: dict[str, float] = {}
        items: dict[str, ResultItem] = {}
        contributions: dict[str, dict[str, dict[str, float | int | str]]] = {}
        for source in (dense_result, sparse_result):
            source_name = source.provenance.get("provider", "unknown")
            score_semantic = source.provenance.get("score_type", "provider_score")
            for rank, item in enumerate(source.items, start=1):
                contribution = 1.0 / (self._rrf_k + rank)
                scores[item.id] = scores.get(item.id, 0.0) + contribution
                items.setdefault(item.id, item)
                contributions.setdefault(item.id, {})[str(source_name)] = {
                    "source_rank": rank,
                    "source_score": item.score,
                    "source_score_semantic": str(score_semantic),
                    "rrf_contribution": contribution,
                }
        ordered_ids = sorted(scores, key=lambda item_id: (-scores[item_id], item_id))
        fusion_limit = int(plan.parameters.get("fusion_candidate_k", plan.parameters.get("retrieval_candidate_k", plan.top_k)))
        fused = tuple(items[item_id].with_score(scores[item_id], signals={"rrf": scores[item_id]}) for item_id in ordered_ids[:fusion_limit])
        fusion_latency_ms = (time.perf_counter() - fusion_started) * 1000
        fusion_candidates = {
            item_id: {**values, "total_fused_score": scores[item_id], "fusion_rank": rank, "deduplicated": len(values) > 1}
            for rank, item_id in enumerate(ordered_ids[:fusion_limit], start=1)
            for values in [contributions[item_id]]
        }
        return RetrievalResult(
            items=fused,
            plan_id=plan.plan_id,
            strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={
                "retrievers": [self._sparse.name, self._dense.name],
                "fusion": "reciprocal_rank_fusion",
                "rrf_k": self._rrf_k,
                "fusion_candidate_k": fusion_limit,
                "fusion_latency_ms": fusion_latency_ms,
                "fusion_candidates": fusion_candidates,
            },
            trace=(f"retrieved:{self._sparse.name}", f"retrieved:{self._dense.name}", "fused:rrf"),
        )
