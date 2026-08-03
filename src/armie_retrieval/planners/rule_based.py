"""MVP planner: capability-aware rules producing declarative plans."""

from __future__ import annotations

from armie_retrieval.models.domain import Policy, Query, RetrievalPlan


class RuleBasedPlanner:
    def __init__(
        self,
        available_capabilities: frozenset[str],
        policy: Policy | None = None,
        *,
        strategy_override: str | None = None,
        processor_names: tuple[str, ...] | None = None,
        parameters: dict[str, object] | None = None,
    ) -> None:
        self._capabilities = available_capabilities
        self._policy = policy
        self._strategy_override = strategy_override
        self._processor_names = processor_names
        self._parameters = dict(parameters or {})

    def plan(self, query: Query) -> RetrievalPlan:
        text = query.text.lower()
        graph_intent = any(token in text for token in ("relationship", "connected", "network", "ecosystem", "path"))
        if self._strategy_override is not None:
            if self._strategy_override not in self._capabilities:
                raise ValueError(f"Requested strategy is unavailable: {self._strategy_override}")
            strategy = self._strategy_override
        elif graph_intent and "graph" in self._capabilities:
            strategy = "graph"
        elif {"dense", "sparse"} <= self._capabilities:
            strategy = "hybrid"
        else:
            strategy = "dense"
        processors: list[str] = list(self._processor_names) if self._processor_names is not None else ["deduplicate"]
        if query.filters and self._processor_names is None:
            processors.append("metadata_filter")
        if self._processor_names is None:
            policy_processors = self._policy.processor_defaults if self._policy else ("expert_rerank",)
            for processor in policy_processors:
                if processor not in processors:
                    processors.append(processor)
        parameters = dict(self._policy.planner_defaults) if self._policy else {"candidate_multiplier": 3}
        parameters.update(self._parameters)
        parameters.setdefault("candidate_multiplier", 3)
        return RetrievalPlan(
            strategy=strategy,
            processor_names=tuple(processors),
            top_k=query.top_k,
            filters=query.filters,
            parameters=parameters,
        )
