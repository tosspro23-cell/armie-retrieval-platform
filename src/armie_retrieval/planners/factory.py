"""Configuration-led planner selection with stable downstream contracts."""

from __future__ import annotations

from typing import Any, Mapping

from armie_retrieval.models.domain import Policy
from armie_retrieval.planners.llm import LLMPlanner, StructuredLLMClient
from armie_retrieval.planners.rule_based import RuleBasedPlanner


def create_planner(
    config: Mapping[str, Any], *, available_capabilities: frozenset[str], policy: Policy | None = None,
    llm_client: StructuredLLMClient | None = None,
):
    planner_type = config.get("planner", {}).get("type", "rule")
    if planner_type == "rule":
        return RuleBasedPlanner(available_capabilities, policy)
    if planner_type == "llm":
        if llm_client is None:
            raise ValueError("LLM planner selected but no StructuredLLMClient was supplied")
        return LLMPlanner(llm_client, available_capabilities, policy)
    raise ValueError(f"Unsupported planner type: {planner_type}")
