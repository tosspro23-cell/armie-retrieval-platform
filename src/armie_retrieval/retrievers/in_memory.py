"""Deterministic in-memory retrievers used by the portable MVP."""

from __future__ import annotations

import math
import re
import time
from collections import Counter
from armie_retrieval.models.domain import Query, RetrievalPlan, RetrievalResult, ResultItem
from armie_retrieval.providers import InMemoryKnowledgeProvider

TOKEN = re.compile(r"[a-z0-9]+")


def candidate_limit(plan: RetrievalPlan) -> int:
    """Plan-visible retrieval boundary; legacy candidate_multiplier remains compatible."""
    return int(plan.parameters.get("retrieval_candidate_k", plan.top_k * int(plan.parameters.get("candidate_multiplier", 1))))


def _tokens(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def _text(item: ResultItem) -> str:
    return " ".join([item.title, item.content, *map(str, item.metadata.values())])


class _BaseInMemoryRetriever:
    def __init__(self, provider: InMemoryKnowledgeProvider) -> None:
        self._provider = provider

    @staticmethod
    def _result(plan: RetrievalPlan, started: float, items: list[ResultItem], source: str) -> RetrievalResult:
        return RetrievalResult(
            items=tuple(items), plan_id=plan.plan_id, strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={"retrievers": [source]}, trace=(f"retrieved:{source}",),
        )


class SparseRetriever(_BaseInMemoryRetriever):
    """A transparent lexical scorer standing in for BM25 in the dependency-free MVP."""

    name = "sparse"

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        query_terms = Counter(_tokens(query.text))
        scored: list[ResultItem] = []
        for item in self._provider.items():
            terms = Counter(_tokens(_text(item)))
            score = sum(min(count, terms[term]) for term, count in query_terms.items())
            if score:
                scored.append(item.with_score(float(score), signals={"sparse": float(score)}))
        scored.sort(key=lambda value: value.score, reverse=True)
        return self._result(plan, started, scored[: candidate_limit(plan)], self.name)


class DenseRetriever(_BaseInMemoryRetriever):
    """Hashing-vector cosine similarity; replaceable with a model/vector provider."""

    name = "dense"
    _dimensions = 64

    def _vector(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        for term in _tokens(text):
            vector[hash(term) % self._dimensions] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        qvector = self._vector(query.text)
        scored: list[ResultItem] = []
        for item in self._provider.items():
            score = sum(left * right for left, right in zip(qvector, self._vector(_text(item))))
            if score > 0:
                scored.append(item.with_score(score, signals={"dense": score}))
        scored.sort(key=lambda value: value.score, reverse=True)
        return self._result(plan, started, scored[: candidate_limit(plan)], self.name)


class HybridRetriever:
    """Coordinates strategies and uses RRF for score-scale-independent fusion."""

    name = "hybrid"

    def __init__(self, dense: DenseRetriever, sparse: SparseRetriever, *, rrf_k: int = 60) -> None:
        self._dense = dense
        self._sparse = sparse
        self._rrf_k = rrf_k

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        sources = (self._dense.retrieve(query, plan), self._sparse.retrieve(query, plan))
        scores: dict[str, float] = {}
        items: dict[str, ResultItem] = {}
        for source in sources:
            for rank, item in enumerate(source.items, start=1):
                scores[item.id] = scores.get(item.id, 0.0) + 1 / (self._rrf_k + rank)
                items[item.id] = item
        fused = [items[item_id].with_score(score, signals={"rrf": score}) for item_id, score in scores.items()]
        fused.sort(key=lambda value: value.score, reverse=True)
        return RetrievalResult(
            items=tuple(fused), plan_id=plan.plan_id, strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={"retrievers": ["dense", "sparse"], "fusion": "rrf"},
            trace=("retrieved:dense", "retrieved:sparse", "fused:rrf"),
        )
