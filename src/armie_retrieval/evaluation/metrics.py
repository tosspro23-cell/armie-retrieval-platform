"""Offline-friendly retrieval metrics; evaluation observes but does not mutate results."""

from __future__ import annotations

from math import log2

from armie_retrieval.models.domain import EvaluationResult, RetrievalResult


DEFAULT_CUTOFFS = (1, 2, 3, 5, 10)


def evaluate(result: RetrievalResult, relevant_ids: set[str], k: int = 5) -> EvaluationResult:
    metrics, _ = evaluate_with_explanation(result, relevant_ids, k=k)
    return metrics


def evaluate_with_explanation(result: RetrievalResult, relevant_ids: set[str], k: int = 5) -> tuple[EvaluationResult, dict]:
    """Calculate metrics and their arithmetic basis from one shared code path."""
    selected = result.items[:k]
    hits = [item.id for item in selected if item.id in relevant_ids]
    precision = len(hits) / k if k else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    reciprocal_rank = next((1 / rank for rank, item in enumerate(selected, 1) if item.id in relevant_ids), 0.0)
    dcg = sum(
        1 / log2(rank + 1)
        for rank, item in enumerate(selected, 1)
        if item.id in relevant_ids
    )
    ideal_count = min(len(relevant_ids), k)
    ideal_dcg = sum(1 / log2(rank + 1) for rank in range(1, ideal_count + 1))
    ndcg = dcg / ideal_dcg if ideal_dcg else 0.0
    metric = EvaluationResult(precision, recall, reciprocal_rank, result.latency_ms, len(result.items), ndcg)
    relevance_vector = [1 if item.id in relevant_ids else 0 for item in selected]
    return metric, {
        "retrieved_ids": [item.id for item in selected],
        "relevant_ids": sorted(relevant_ids),
        "relevant_retrieved_ids": hits,
        "precision": {"numerator": len(hits), "denominator": k, "value": precision},
        "recall": {"numerator": len(hits), "denominator": len(relevant_ids), "value": recall},
        "mrr": {"first_relevant_rank": next((rank for rank, item in enumerate(selected, 1) if item.id in relevant_ids), None), "value": reciprocal_rank},
        "ndcg": {"relevance_vector": relevance_vector, "dcg": dcg, "ideal_relevance_vector": [1] * ideal_count, "idcg": ideal_dcg, "value": ndcg},
        "latency_ms": result.latency_ms,
    }


def evaluate_at_cutoffs(
    result: RetrievalResult, relevant_ids: set[str], cutoffs: tuple[int, ...] = DEFAULT_CUTOFFS,
) -> tuple[dict[str, float], dict]:
    """Calculate all rendered metrics through the same per-K implementation."""
    metrics: dict[str, float] = {}
    arithmetic: dict[str, dict] = {}
    for k in cutoffs:
        metric, explanation = evaluate_with_explanation(result, relevant_ids, k=k)
        metrics.update({
            f"precision_at_{k}": metric.precision_at_k,
            f"recall_at_{k}": metric.recall_at_k,
            f"ndcg_at_{k}": metric.ndcg_at_k,
        })
        arithmetic[str(k)] = {
            **explanation,
            "maximum_possible_precision": min(len(relevant_ids), k) / k if k else 0.0,
            "note": (
                f"With {len(relevant_ids)} labeled relevant IDs, maximum Precision@{k} is "
                f"{min(len(relevant_ids), k)}/{k}={min(len(relevant_ids), k) / k:.4f}."
                if k else "Precision@0 is defined as 0."
            ),
        }
    metrics["mrr"] = evaluate_with_explanation(result, relevant_ids, k=max(cutoffs, default=1))[0].reciprocal_rank
    metrics["latency_ms"] = result.latency_ms
    return metrics, {"cutoffs": arithmetic, "total_relevant_count": len(relevant_ids)}
