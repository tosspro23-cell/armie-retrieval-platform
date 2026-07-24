"""LLM-compatible declarative planner. The client is injected, never a provider."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from armie_retrieval.models.domain import Policy, Query, RetrievalPlan


class StructuredLLMClient(Protocol):
    def complete(self, *, prompt: str) -> Mapping[str, Any]:
        """Return a validated structured planning response from an LLM."""


class LLMPlanner:
    """Transforms a structured LLM decision into the same immutable RetrievalPlan."""

    _allowed_strategies = frozenset({"dense", "sparse", "hybrid", "graph"})

    def __init__(self, client: StructuredLLMClient, available_capabilities: frozenset[str], policy: Policy | None = None) -> None:
        self._client = client
        self._capabilities = available_capabilities
        self._policy = policy

    def plan(self, query: Query) -> RetrievalPlan:
        response = self._client.complete(prompt=self._prompt(query))
        strategy = str(response.get("strategy", "dense"))
        if strategy not in self._allowed_strategies or strategy not in self._capabilities:
            strategy = "dense" if "dense" in self._capabilities else next(iter(self._capabilities))
        processors = tuple(str(item) for item in response.get("processors", ("deduplicate", "expert_rerank")))
        return RetrievalPlan(
            strategy=strategy,
            processor_names=processors,
            top_k=max(1, int(response.get("top_k", query.top_k))),
            filters=dict(response.get("filters", query.filters)),
            constraints=dict(response.get("constraints", {})),
            parameters=dict(response.get("parameters", self._policy.planner_defaults if self._policy else {"candidate_multiplier": 3})),
        )

    def _prompt(self, query: Query) -> str:
        return (
            "Create a declarative retrieval plan. Do not select a provider, SDK, index, or API. "
            f"Capabilities: {sorted(self._capabilities)}. Query: {query.text!r}. "
            f"Filters: {dict(query.filters)}. Return strategy, processors, top_k, filters, constraints, parameters."
        )
