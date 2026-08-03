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
        payload = {"knn": {"field": "embedding", "query_vector": vector, "k": int(plan.parameters.get("retrieval_candidate_k", plan.top_k)), "num_candidates": int(plan.parameters.get("retrieval_candidate_k", plan.top_k) * 2)}}
        hits = self.client.request("POST", f"{self.index}/_search", json=payload).json().get("hits", {}).get("hits", [])
        return self._result(query, plan, hits, started, "elasticsearch_dense_score")
