"""Graded relevance metrics used by the v0.4.0 benchmark layer."""

from __future__ import annotations

from math import log2
from typing import Mapping, Sequence


def graded_metrics(result_ids: Sequence[str], grades: Mapping[str, int], *, k: int = 5) -> dict[str, float | int | None]:
    selected = list(result_ids[:k])
    relevance = [max(0, int(grades.get(item_id, 0))) for item_id in selected]
    relevant_ids = {item_id for item_id, grade in grades.items() if grade > 0}
    hits = sum(grade > 0 for grade in relevance)
    precision = hits / k if k else 0.0
    recall = hits / len(relevant_ids) if relevant_ids else 0.0
    first = next((index for index, grade in enumerate(relevance, 1) if grade > 0), None)
    mrr = 1 / first if first else 0.0
    dcg = sum((2 ** grade - 1) / log2(index + 1) for index, grade in enumerate(relevance, 1))
    ideal = sorted((max(0, int(grade)) for grade in grades.values()), reverse=True)[:k]
    idcg = sum((2 ** grade - 1) / log2(index + 1) for index, grade in enumerate(ideal, 1))
    return {
        "precision_at_k": precision,
        "recall_at_k": recall,
        "mrr": mrr,
        "ndcg_at_k": dcg / idcg if idcg else 0.0,
        "first_relevant_rank": first,
        "grade_3_hit": int(any(grade == 3 for grade in relevance)),
        "hard_negative_intrusion": int(any(grade == 0 for grade in relevance)),
        "labelled_relevant_count": len(relevant_ids),
    }
