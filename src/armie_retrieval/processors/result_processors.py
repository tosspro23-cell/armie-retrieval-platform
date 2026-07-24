"""Ordered, plan-selected transformations of a RetrievalResult."""

from __future__ import annotations

from armie_retrieval.models.domain import RetrievalPlan, RetrievalResult


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
    """Domain MVP reranker: rewards exact metadata matches without hiding base score."""

    name = "expert_rerank"

    def process(self, result: RetrievalResult, plan: RetrievalPlan) -> RetrievalResult:
        boosted = []
        for item in result.items:
            boost = sum(0.05 for key, value in plan.filters.items() if str(item.metadata.get(key, "")).lower() == str(value).lower())
            boosted.append(item.with_score(item.score + boost, signals={**item.signals, "rerank_boost": boost}))
        boosted.sort(key=lambda item: item.score, reverse=True)
        return result.with_items(tuple(boosted[: plan.top_k]), "processed:expert_rerank")
