"""GraphRetriever executes a declarative `graph` strategy against NetworkX."""

from __future__ import annotations

import re
import time

from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult, ResultItem
from armie_retrieval.providers.knowledge_graph import NetworkXKnowledgeGraphProvider
from armie_retrieval.retrievers.in_memory import candidate_limit

TOKEN = re.compile(r"[a-z0-9]+")


class GraphRetriever:
    name = "graph"
    capabilities = frozenset({"graph"})

    def __init__(self, provider: NetworkXKnowledgeGraphProvider) -> None:
        self._provider = provider

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        terms = set(TOKEN.findall(query.text.lower()))
        scores: dict[str, float] = {}
        graph = self._provider.graph
        for node_id, attributes in graph.nodes(data=True):
            node_terms = set(TOKEN.findall(str(attributes.get("label", "")).lower()))
            overlap = len(terms & node_terms)
            if not overlap:
                continue
            if attributes.get("node_type") == "Person":
                scores[node_id] = scores.get(node_id, 0.0) + overlap
            for neighbor in graph.neighbors(node_id):
                if neighbor in self._provider.expert_items():
                    scores[neighbor] = scores.get(neighbor, 0.0) + overlap
        items: list[ResultItem] = []
        for expert_id, score in scores.items():
            expert = self._provider.expert_items().get(expert_id)
            if expert:
                items.append(expert.with_score(score, signals={"graph": score}))
        items.sort(key=lambda item: item.score, reverse=True)
        return RetrievalResult(
            items=tuple(items[:candidate_limit(plan)]), plan_id=plan.plan_id, strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={"retrievers": [self.name], "provider": self._provider.name},
            trace=("retrieved:graph",),
        )
