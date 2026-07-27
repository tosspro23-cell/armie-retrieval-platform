"""High-level trace session that composes existing planner, runtime, and evaluator APIs."""

from __future__ import annotations

import re
import time
from dataclasses import asdict
from typing import Any, Mapping

from armie_retrieval.evaluation import DEFAULT_CUTOFFS, evaluate_at_cutoffs, evaluate_with_explanation
from armie_retrieval.models import Query, RetrievalPlan
from armie_retrieval.planners.metadata import planner_metadata, routing_warnings

from .collector import TraceCollector
from .models import EvaluationTrace, GroundTruthTrace, PlannerTrace, RetrievalTrace


def trace_query(runtime, planner, query: Query, *, query_id: str | None = None, relevant_ids: set[str] | None = None, evaluation_cutoffs: tuple[int, ...] = DEFAULT_CUTOFFS) -> tuple[object, RetrievalTrace]:
    """Execute exactly one normal runtime request with optional structured tracing."""
    plan, planner_trace = capture_plan(planner, query)
    collector = TraceCollector(query, plan, planner_trace, query_id=query_id)
    result = runtime.execute_with_trace(query, plan, collector)
    ground_truth = _ground_truth(query_id, relevant_ids, result)
    evaluation_trace = None
    if relevant_ids is not None:
        metric, calculation = evaluate_with_explanation(result, relevant_ids, k=query.top_k)
        multi_metrics, multi_calculation = evaluate_at_cutoffs(result, relevant_ids, evaluation_cutoffs)
        evaluation_trace = EvaluationTrace({**asdict(metric), **multi_metrics}, {**calculation, "multi_k": multi_calculation})
    return result, collector.build(ground_truth=ground_truth, evaluation=evaluation_trace)


def capture_plan(planner, query: Query) -> tuple[RetrievalPlan, PlannerTrace]:
    """Capture structured planner decisions only; never chain-of-thought."""
    started = time.perf_counter()
    raw_output: Mapping[str, Any] | None = None
    warnings: list[str] = []
    try:
        if hasattr(planner, "plan_with_trace"):
            plan, raw_output = planner.plan_with_trace(query)
        else:
            plan = planner.plan(query)
    except Exception as exc:
        raise RuntimeError(f"Planner execution failed: {exc}") from exc
    fallback = None
    if raw_output and str(raw_output.get("strategy", plan.strategy)) != plan.strategy:
        fallback = f"Requested strategy {raw_output.get('strategy')!r} resolved to {plan.strategy!r}"
    planner_name = type(planner).__name__
    client = getattr(planner, "_client", None)
    model = getattr(client, "model", None)
    selection = getattr(planner, "selection", None)
    requested_provider = getattr(selection, "requested", planner_name)
    actual_provider = getattr(selection, "actual", planner_name)
    requested_model = getattr(selection, "requested_model", model)
    fallback_enabled = bool(getattr(selection, "fallback_enabled", False))
    fallback_reason = getattr(planner, "last_fallback_reason", None) or getattr(selection, "fallback_reason", None)
    fallback_diagnostic = getattr(planner, "last_fallback_diagnostic", None)
    if fallback_reason:
        fallback = fallback_reason
        actual_provider = "rule" if requested_provider == "ollama" else actual_provider
    metadata, metadata_warnings = planner_metadata(raw_output, query)
    selected_retrievers = ("dense", "sparse") if plan.strategy == "hybrid" else (plan.strategy,)
    warnings.extend(metadata_warnings)
    warnings.extend(routing_warnings(strategy=plan.strategy, selected_retrievers=selected_retrievers, metadata=metadata))
    capabilities = {
        "dense": "semantic similarity and paraphrase retrieval",
        "sparse": "exact lexical and named-term retrieval",
        "graph": "entity relationship and structured constraint retrieval",
    }
    return plan, PlannerTrace(
        raw_query=query.text,
        provider=actual_provider,
        model=requested_model or model,
        raw_output=raw_output,
        parsed_plan=asdict(plan),
        selected_strategy=plan.strategy,
        selected_retrievers=selected_retrievers,
        extracted_skills=metadata["skills"],
        extracted_industries=metadata["industries"],
        extracted_organizations=metadata["organizations"],
        filters=dict(plan.filters),
        constraints=dict(plan.constraints),
        requested_top_k=plan.top_k,
        fallback=fallback,
        warnings=tuple(warnings),
        latency_ms=(time.perf_counter() - started) * 1000,
        requested_provider=requested_provider,
        actual_provider=actual_provider,
        requested_model=requested_model,
        fallback_enabled=fallback_enabled,
        fallback_reason=fallback_reason,
        reason_codes=metadata["reason_codes"],
        constraint_types=metadata["constraint_types"],
        requested_retrievers=metadata["requested_retrievers"],
        available_capabilities=capabilities,
        planner_requested_top_k=plan.top_k,
        retrieval_candidate_k=int(plan.parameters.get("retrieval_candidate_k", plan.top_k)),
        rerank_candidate_k=int(plan.parameters.get("rerank_candidate_k", plan.top_k)),
        effective_final_top_k=int(plan.parameters.get("final_top_k", plan.top_k)),
        effective_top_k_source=str(plan.parameters.get("effective_top_k_source", "planner")),
        fallback_diagnostic=fallback_diagnostic,
    )


def _ground_truth(query_id: str | None, relevant_ids: set[str] | None, result) -> GroundTruthTrace | None:
    if relevant_ids is None:
        return None
    retrieved = tuple(item.id for item in result.items)
    relevant = tuple(sorted(relevant_ids))
    relevant_retrieved = tuple(item_id for item_id in retrieved if item_id in relevant_ids)
    first_rank = next((rank for rank, item_id in enumerate(retrieved, 1) if item_id in relevant_ids), None)
    return GroundTruthTrace(
        query_id=query_id or result.plan_id,
        relevant_ids=relevant,
        retrieved_ids=retrieved,
        relevant_retrieved_ids=relevant_retrieved,
        missed_relevant_ids=tuple(item_id for item_id in relevant if item_id not in retrieved),
        non_relevant_ids=tuple(item_id for item_id in retrieved if item_id not in relevant_ids),
        first_relevant_rank=first_rank,
    )


def _phrases(text: str, known_phrases: tuple[str, ...]) -> tuple[str, ...]:
    normalized = re.sub(r"\s+", " ", text.lower())
    return tuple(phrase for phrase in known_phrases if phrase in normalized)
