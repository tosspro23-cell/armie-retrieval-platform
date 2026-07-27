"""Compose profiles into explicit planner, reranker, and policy selections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from armie_retrieval.models import Policy
from armie_retrieval.planners import RuleBasedPlanner, create_planner
from armie_retrieval.planners.ollama import OllamaPrerequisiteError
from armie_retrieval.rerankers import RerankerSelection, create_reranker


@dataclass(frozen=True)
class PlannerSelection:
    planner: object
    requested: str
    actual: str
    requested_model: str | None
    fallback_enabled: bool
    fallback_reason: str | None = None


class ControlledFallbackPlanner:
    """Uses an explicit fallback only when the requested planner fails at execution."""

    def __init__(self, primary, fallback, selection: PlannerSelection) -> None:
        self._primary = primary
        self._fallback = fallback
        self.selection = selection
        self.last_fallback_reason: str | None = None
        self.last_fallback_diagnostic = None

    def plan(self, query):
        plan, _ = self.plan_with_trace(query)
        return plan

    def plan_with_trace(self, query):
        try:
            self.last_fallback_reason = None
            self.last_fallback_diagnostic = None
            if hasattr(self._primary, "plan_with_trace"):
                return self._primary.plan_with_trace(query)
            return self._primary.plan(query), None
        except Exception as exc:
            self.last_fallback_reason = str(exc)
            self.last_fallback_diagnostic = getattr(exc, "diagnostic", {
                "fallback_type": "planner_runtime_failure", "fallback_stage": "planner_execution",
                "fallback_reason": str(exc), "internal_error": repr(exc),
            })
            return self._fallback.plan(query), None


def profile_policy(profile: Mapping[str, Any]) -> Policy:
    pool = profile.get("candidate_pool", {})
    return Policy(
        version=1,
        planner_defaults={
            "candidate_multiplier": 3,
            "retrieval_candidate_k": int(pool.get("retrieval_candidate_k", 20)),
            "rerank_candidate_k": int(pool.get("rerank_candidate_k", 20)),
            "final_top_k": int(pool.get("final_top_k", 5)),
            "effective_top_k_source": str(pool.get("effective_top_k_source", f"profile:{profile.get('name', 'unknown')}")),
        },
        processor_defaults=("rerank",),
    )


def select_planner(profile: Mapping[str, Any], *, capabilities: frozenset[str], llm_client=None) -> PlannerSelection:
    config = dict(profile.get("planner", {}))
    requested = str(config.get("type", "rule"))
    requested = {"rule-based": "rule", "ollama": "llm"}.get(requested, requested)
    model = config.get("model")
    policy = profile_policy(profile)
    if requested == "rule":
        planner = RuleBasedPlanner(capabilities, policy)
        selection = PlannerSelection(planner, "rule", "rule", None, False)
        planner.selection = selection
        return selection
    factory_config = {"planner": {"type": "llm", "ollama": {
        "model": model, "base_url": config.get("base_url", "http://127.0.0.1:11434"),
        "timeout_seconds": config.get("timeout_seconds", 90),
    }}}
    try:
        planner = create_planner(factory_config, available_capabilities=capabilities, policy=policy, llm_client=llm_client)
        selection = PlannerSelection(planner, "ollama", "ollama", model, bool(config.get("fallback_enabled", False)))
        if selection.fallback_enabled:
            planner = ControlledFallbackPlanner(planner, RuleBasedPlanner(capabilities, policy), selection)
            selection = PlannerSelection(planner, "ollama", "ollama", model, True)
        else:
            planner.selection = selection
        return selection
    except (OllamaPrerequisiteError, ValueError, RuntimeError) as exc:
        if bool(config.get("fallback_enabled", False)) and str(config.get("fallback", "rule")) == "rule":
            return PlannerSelection(RuleBasedPlanner(capabilities, policy), "ollama", "rule", model, True, str(exc))
        raise


def select_reranker(profile: Mapping[str, Any]) -> RerankerSelection:
    return create_reranker(dict(profile.get("reranker", {})))
