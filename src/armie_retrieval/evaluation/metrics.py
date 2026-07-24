"""Offline-friendly retrieval metrics; evaluation observes but does not mutate results."""

from __future__ import annotations

from armie_retrieval.models.domain import EvaluationResult, RetrievalResult


def evaluate(result: RetrievalResult, relevant_ids: set[str], k: int = 5) -> EvaluationResult:
    selected = result.items[:k]
    hits = [item.id for item in selected if item.id in relevant_ids]
    precision = len(hits) / k if k else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    reciprocal_rank = next((1 / rank for rank, item in enumerate(selected, 1) if item.id in relevant_ids), 0.0)
    return EvaluationResult(precision, recall, reciprocal_rank, result.latency_ms, len(result.items))
