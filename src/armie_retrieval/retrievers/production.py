"""Production retrievers that consume persisted artifacts built offline."""

from __future__ import annotations

import time

from armie_retrieval.embeddings import EmbeddingProvider
from armie_retrieval.indexing import KeywordIndex
from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult
from armie_retrieval.vectorstores import FaissVectorStore
from armie_retrieval.retrievers.in_memory import candidate_limit


class FaissDenseRetriever:
    """Dense retrieval over a prebuilt FAISS artifact; it never indexes at runtime."""

    name = "faiss_dense"
    capabilities = frozenset({"dense"})

    def __init__(self, vector_store: FaissVectorStore, embedding_provider: EmbeddingProvider) -> None:
        self._vector_store = vector_store
        self._embedding_provider = embedding_provider

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        candidate_count = candidate_limit(plan)
        vector = self._embedding_provider.embed([query.text])[0]
        items = tuple(
            item.with_score(score, signals={"faiss_dense": score})
            for item, score in self._vector_store.search(vector, candidate_count)
        )
        return RetrievalResult(
            items=items,
            plan_id=plan.plan_id,
            strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={"retrievers": [self.name], "index": "faiss"},
            trace=("retrieved:faiss_dense",),
        )


class IndexedSparseRetriever:
    """Sparse retrieval over a prebuilt keyword-index artifact."""

    name = "indexed_sparse"
    capabilities = frozenset({"sparse"})

    def __init__(self, keyword_index: KeywordIndex) -> None:
        self._keyword_index = keyword_index

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        candidate_count = candidate_limit(plan)
        items = tuple(
            item.with_score(score, signals={"indexed_sparse": score})
            for item, score in self._keyword_index.search(query.text, candidate_count)
        )
        return RetrievalResult(
            items=items,
            plan_id=plan.plan_id,
            strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={"retrievers": [self.name], "index": "keyword"},
            trace=("retrieved:indexed_sparse",),
        )
