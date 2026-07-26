"""Repeatable offline evaluation runner for retrieval benchmark cases."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, Mapping, Protocol

from armie_retrieval.models import EvaluationResult, Query

from .metrics import evaluate


class ExecutableRuntime(Protocol):
    def execute(self, query: Query, plan): ...


class Planner(Protocol):
    def plan(self, query: Query): ...


@dataclass(frozen=True)
class EvaluationRun:
    case_results: Mapping[str, EvaluationResult]
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    latency_ms: float


def run_evaluation(runtime: ExecutableRuntime, planner: Planner, cases: Iterable[Mapping], *, top_k: int = 5) -> EvaluationRun:
    """Evaluate benchmark cases without mutating plans or retrieval results."""
    case_results: dict[str, EvaluationResult] = {}
    for case in cases:
        query = Query(str(case["query"]), top_k=top_k)
        result = runtime.execute(query, planner.plan(query))
        case_results[str(case["id"])] = evaluate(result, set(case["relevant_ids"]), k=top_k)
    metrics = tuple(case_results.values())
    if not metrics:
        raise ValueError("Evaluation requires at least one benchmark case")
    return EvaluationRun(
        case_results=case_results,
        precision_at_k=mean(metric.precision_at_k for metric in metrics),
        recall_at_k=mean(metric.recall_at_k for metric in metrics),
        mrr=mean(metric.reciprocal_rank for metric in metrics),
        ndcg_at_k=mean(metric.ndcg_at_k for metric in metrics),
        latency_ms=mean(metric.latency_ms for metric in metrics),
    )
