"""Explicit failure taxonomy for relevance engineering reports."""

from __future__ import annotations

from enum import Enum
from typing import Mapping


class FailureCode(str, Enum):
    dataset_missing_evidence = "dataset_missing_evidence"
    schema_modelling_gap = "schema_modelling_gap"
    lexical_mismatch = "lexical_mismatch"
    semantic_false_positive = "semantic_false_positive"
    filter_failure = "filter_failure"
    constraint_violation = "constraint_violation"
    employer_client_ambiguity = "employer_client_ambiguity"
    delivery_mention_ambiguity = "delivery_mention_ambiguity"
    fusion_displacement = "fusion_displacement"
    reranker_regression = "reranker_regression"
    candidate_pool_miss = "candidate_pool_miss"
    stale_experience = "stale_experience"
    near_duplicate = "near_duplicate"
    judgement_gap = "judgement_gap"
    planner_routing_error = "planner_routing_error"
    backend_inconsistency = "backend_inconsistency"
    graph_relationship_needed = "graph_relationship_needed"


def classify_failure(query_text: str, result_ids: list[str], grades: Mapping[str, int], *, stage: str = "retrieval") -> tuple[FailureCode, ...]:
    failures: list[FailureCode] = []
    if not result_ids:
        failures.append(FailureCode.candidate_pool_miss)
    if result_ids and not any(grades.get(item_id, 0) > 0 for item_id in result_ids):
        failures.append(FailureCode.semantic_false_positive if stage == "dense" else FailureCode.lexical_mismatch)
    lowered = query_text.lower()
    if "worked at" in lowered and "project" in lowered:
        failures.append(FailureCode.employer_client_ambiguity)
    if "implemented" in lowered or "delivered" in lowered:
        failures.append(FailureCode.delivery_mention_ambiguity)
    return tuple(dict.fromkeys(failures))
