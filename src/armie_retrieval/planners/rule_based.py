"""MVP planner: capability-aware rules producing declarative plans."""

from __future__ import annotations

from armie_retrieval.models.domain import Policy, Query, RetrievalPlan


class RuleBasedPlanner:
    def __init__(self, available_capabilities: frozenset[str], policy: Policy | None = None) -> None:
        self._capabilities = available_capabilities
        self._policy = policy

    def plan(self, query: Query) -> RetrievalPlan:
        text = query.text.lower()
        graph_intent = any(token in text for token in ("relationship", "connected", "network", "ecosystem", "path"))
        if graph_intent and "graph" in self._capabilities:
            strategy = "graph"
        elif {"dense", "sparse"} <= self._capabilities:
            strategy = "hybrid"
        else:
            strategy = "dense"
        processors: list[str] = ["deduplicate"]
        if query.filters:
            processors.append("metadata_filter")
        policy_processors = self._policy.processor_defaults if self._policy else ("expert_rerank",)
        for processor in policy_processors:
            if processor not in processors:
                processors.append(processor)
        parameters = dict(self._policy.planner_defaults) if self._policy else {"candidate_multiplier": 3}
        parameters.setdefault("candidate_multiplier", 3)
        return RetrievalPlan(
            strategy=strategy,
            processor_names=tuple(processors),
            top_k=query.top_k,
            filters=query.filters,
            parameters=parameters,
        )
