"""Ordered, plan-selected transformations of a RetrievalResult."""

from __future__ import annotations

from armie_retrieval.models.domain import RetrievalPlan, RetrievalResult
from armie_retrieval.rerankers import MetadataBoostReranker, RerankerProvider


class DeduplicateProcessor:
    name = "deduplicate"

    def process(self, result: RetrievalResult, plan: RetrievalPlan) -> RetrievalResult:
        unique = {item.id: item for item in result.items}
        return result.with_items(tuple(unique.values()), "processed:deduplicate")


class MetadataFilterProcessor:
    name = "metadata_filter"

    def process(self, result: RetrievalResult, plan: RetrievalPlan) -> RetrievalResult:
        def matches(item) -> bool:
            return all(str(item.metadata.get(key, "")).lower() == str(value).lower() for key, value in plan.filters.items())
        return result.with_items(tuple(item for item in result.items if matches(item)), "processed:metadata_filter")


class ExpertRerankProcessor:
    """Backward-compatible metadata boost processor (not a neural reranker)."""

    name = "expert_rerank"

    def process(self, result: RetrievalResult, plan: RetrievalPlan) -> RetrievalResult:
        return RerankProcessor(MetadataBoostReranker(), name=self.name).process(result, plan)


class RerankProcessor:
    """Result Processor adapter around an explicit reranker provider.

    Candidate-pool and final Top-K boundaries remain visible in the immutable plan.
    """

    def __init__(self, reranker: RerankerProvider, *, name: str = "rerank") -> None:
        self._reranker = reranker
        self.name = name
        self.last_rerank_result = None
        self.last_input_items = ()

    def process(self, result: RetrievalResult, plan: RetrievalPlan) -> RetrievalResult:
        rerank_candidate_k = int(plan.parameters.get("rerank_candidate_k", plan.top_k))
        final_top_k = int(plan.parameters.get("final_top_k", plan.top_k))
        bounded = result.items[:rerank_candidate_k]
        self.last_input_items = bounded
        reranked = self._reranker.rerank(QueryProxy(plan), bounded, final_top_k)
        self.last_rerank_result = reranked
        items = tuple(
            row.item.with_score(row.raw_relevance_score, signals={**row.item.signals, "rerank": row.raw_relevance_score})
            for row in reranked.items
        )
        return result.with_items(items, f"processed:{self.name}")


class QueryProxy:
    """The reranker needs query filters; runtime supplies the original Query via `bind_query`."""

    def __init__(self, plan: RetrievalPlan) -> None:
        self.text = ""
        self.filters = plan.filters


class QueryAwareRerankProcessor(RerankProcessor):
    """RerankProcessor bound to a request by the runtime without changing its public contract."""

    def bind_query(self, query) -> None:
        self._query = query

    def process(self, result: RetrievalResult, plan: RetrievalPlan) -> RetrievalResult:
        rerank_candidate_k = int(plan.parameters.get("rerank_candidate_k", plan.top_k))
        final_top_k = int(plan.parameters.get("final_top_k", plan.top_k))
        bounded = result.items[:rerank_candidate_k]
        self.last_input_items = bounded
        original = getattr(self, "_query", QueryProxy(plan))
        query = QueryProxy(plan)
        query.text = getattr(original, "text", "")
        reranked = self._reranker.rerank(query, bounded, final_top_k)
        self.last_rerank_result = reranked
        items = tuple(row.item.with_score(row.raw_relevance_score, signals={**row.item.signals, "rerank": row.raw_relevance_score}) for row in reranked.items)
        return result.with_items(items, f"processed:{self.name}")
