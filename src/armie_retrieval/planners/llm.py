"""LLM-compatible declarative planner. The client is injected, never a provider."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from armie_retrieval.models.domain import Policy, Query, RetrievalPlan
from armie_retrieval.planners.metadata import CONSTRAINT_TYPES, REASON_CODES


class StructuredLLMClient(Protocol):
    def complete(self, *, prompt: str) -> Mapping[str, Any]:
        """Return a validated structured planning response from an LLM."""


class PlannerStructuredOutputError(ValueError):
    """Actionable validation error for imperfect local-model JSON output."""

    def __init__(self, field: str, expected: str, actual: object, *, reason: str | None = None) -> None:
        actual_type = type(actual).__name__ if actual is not None else "null"
        message = reason or f"Planner returned an invalid {expected} for {field}."
        super().__init__(message)
        self.diagnostic = {
            "fallback_type": "structured_output_validation_error", "fallback_stage": "planner_response_parsing",
            "fallback_field": field, "expected_type": expected, "actual_type": actual_type,
            "fallback_reason": message, "internal_error": message,
        }


class LLMPlanner:
    """Transforms a structured LLM decision into the same immutable RetrievalPlan."""

    _allowed_strategies = frozenset({"dense", "sparse", "hybrid", "graph"})
    _allowed_processors = frozenset({"deduplicate", "metadata_filter", "expert_rerank", "rerank"})

    def __init__(self, client: StructuredLLMClient, available_capabilities: frozenset[str], policy: Policy | None = None) -> None:
        self._client = client
        self._capabilities = available_capabilities
        self._policy = policy

    def plan(self, query: Query) -> RetrievalPlan:
        response = self._client.complete(prompt=self._prompt(query))
        return self._plan_from_response(query, response)

    def plan_with_trace(self, query: Query) -> tuple[RetrievalPlan, Mapping[str, Any]]:
        """Optional structured-output capture for observability; no hidden reasoning is exposed."""
        response = self._client.complete(prompt=self._prompt(query))
        return self._plan_from_response(query, response), response

    def _plan_from_response(self, query: Query, response: Mapping[str, Any]) -> RetrievalPlan:
        if not isinstance(response, Mapping):
            raise PlannerStructuredOutputError("response", "object", response)
        strategy = str(response.get("strategy", "dense"))
        # Strategy fallback is part of the established declarative planner
        # contract.  It remains visible through raw output versus parsed plan.
        if strategy not in self._allowed_strategies or strategy not in self._capabilities:
            strategy = "dense" if "dense" in self._capabilities else next(iter(self._capabilities))
        default_processors = ("deduplicate", *(self._policy.processor_defaults if self._policy else ("expert_rerank",)))
        requested_processors = _string_sequence(response.get("processors", default_processors), "processors")
        processors = tuple(item for item in requested_processors if item in self._allowed_processors)
        if not processors:
            processors = default_processors
        parameters = dict(self._policy.planner_defaults) if self._policy else {"candidate_multiplier": 3}
        parameters.update(_mapping(response.get("parameters", {}), "parameters"))
        parameters.setdefault("candidate_multiplier", 3)
        top_k = response.get("top_k", query.top_k)
        if isinstance(top_k, bool) or not isinstance(top_k, int):
            raise PlannerStructuredOutputError("top_k", "positive integer", top_k)
        if top_k < 1:
            raise PlannerStructuredOutputError("top_k", "positive integer", top_k)
        return RetrievalPlan(
            strategy=strategy,
            processor_names=processors,
            top_k=top_k,
            filters=_mapping(response.get("filters", query.filters), "filters"),
            constraints=_mapping(response.get("constraints", {}), "constraints"),
            parameters=parameters,
        )

    def _prompt(self, query: Query) -> str:
        return (
            "Create a declarative retrieval plan and only structured decision metadata; do not expose reasoning, "
            "select a provider, SDK, index, or API. Dense is for semantic similarity, paraphrase, vague natural language, "
            "and concept matching. Sparse is for exact terms, product names, technology names, acronyms, and lexical constraints. "
            "Graph is for entity relationships and graph-representable structured constraints such as skill plus industry or organization. "
            "Hybrid in this runtime means dense plus sparse only; graph remains the separate graph strategy. "
            f"Available strategies: {sorted(self._capabilities)}. Query: {query.text!r}. Filters: {dict(query.filters)}. "
            "Return JSON fields: strategy, retrievers (consistent with strategy), processors, top_k, skills, industries, organizations, "
            "filters, constraints, parameters, reason_codes, constraint_types. "
            f"reason_codes must be selected only from {sorted(REASON_CODES)}. "
            f"constraint_types must be selected only from {sorted(CONSTRAINT_TYPES)}."
        )


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PlannerStructuredOutputError(field, "object", value)
    return dict(value)


def _string_sequence(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise PlannerStructuredOutputError(field, "array", value)
    if not all(isinstance(item, str) for item in value):
        raise PlannerStructuredOutputError(field, "array of strings", value)
    return tuple(value)
