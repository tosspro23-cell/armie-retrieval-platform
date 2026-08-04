"""Independent relevance labels and benchmark-tier utilities.

Labels are derived from structured dataset evidence and query constraints, not
from any profile's returned ranking. The functions are deliberately explicit
so Gold/Silver confidence and synthetic-data limitations remain visible.
"""

from __future__ import annotations

from collections import Counter
from math import log2
from typing import Any, Mapping, Sequence

from armie_retrieval.datasets.models import ExpertProfile
from armie_retrieval.relevance import BenchmarkQuery, Judgement, QueryCategory, draft_judgements


GOLD_COUNTS = {
    QueryCategory.exact_skill: 4,
    QueryCategory.skill_industry: 4,
    QueryCategory.delivery_project: 4,
    QueryCategory.organization: 3,
    QueryCategory.seniority_role: 3,
    QueryCategory.multi_constraint: 4,
    QueryCategory.semantic_paraphrase: 4,
    QueryCategory.hard_negative: 3,
    QueryCategory.temporal: 3,
    QueryCategory.negative_constraint: 3,
}


def select_gold_queries(queries: Sequence[BenchmarkQuery]) -> tuple[BenchmarkQuery, ...]:
    # Stable, stratified selection; no random sampling or retrieval-dependent
    # selection is used.
    selected: list[BenchmarkQuery] = []
    for category, count in GOLD_COUNTS.items():
        selected.extend([query for query in queries if query.category == category][:count])
    return tuple(selected)


def _values(profile: ExpertProfile, name: str) -> set[str]:
    if name == "technology":
        return {value.lower() for value in profile.technologies}
    if name == "industry":
        return {value.lower() for value in profile.industries}
    if name == "employer":
        return {value.organization.lower() for value in profile.employers}
    if name == "role":
        return {value.lower() for value in profile.roles}
    if name == "seniority":
        return {profile.seniority.lower()}
    if name == "location":
        return {value.lower() for value in profile.locations}
    if name == "delivery_evidence":
        return {project.delivery_evidence.lower() for project in profile.projects}
    if name == "delivery_year":
        return {str(project.end_date.year) for project in profile.projects if project.end_date}
    return set()


def independent_judgement(query: BenchmarkQuery, profile: ExpertProfile, *, tier: str = "silver") -> Judgement:
    matched: list[str] = []
    missing: list[str] = []
    violated: list[str] = []
    evidence: list[str] = []
    for constraint in query.required_constraints:
        values = _values(profile, constraint.name)
        if constraint.value.lower() in values:
            matched.append(f"{constraint.name}={constraint.value}")
            evidence.extend(
                project.project_id for project in profile.projects
                if constraint.value.lower() in {project.delivery_evidence.lower(), project.industry.lower(), *(value.lower() for value in project.technologies)}
            )
            evidence.extend(employer.organization for employer in profile.employers if constraint.value.lower() == employer.organization.lower())
        else:
            missing.append(f"{constraint.name}={constraint.value}")
    for constraint in query.prohibited_constraints:
        if constraint.name != "summary_only" and constraint.value.lower() in _values(profile, constraint.name):
            violated.append(f"{constraint.name}={constraint.value}")
    if violated:
        grade, rationale = 0, "prohibited structured constraint is present"
        codes = ["prohibited_constraint"]
    elif not matched:
        grade, rationale = 0, "no independent structured constraint evidence"
        codes = ["no_constraint_evidence"]
    elif not missing:
        grade, rationale = 3, "all required constraints independently verified from structured source evidence"
        codes = ["all_constraints_verified"]
    else:
        grade, rationale = 1, "partial structured constraint evidence; core requirement incomplete"
        codes = ["partial_constraint_evidence"]
    correction_history: list[dict[str, Any]] = []
    if tier == "gold":
        draft = draft_judgements((query,), (profile,))[0]
        correction_history.append({
            "action": "independent_structured_review",
            "previous_status": "rule_assisted_draft",
            "changed": draft.grade != grade or set(draft.violated_constraints) != set(violated),
            "reason": "recomputed from structured constraints and source evidence outside the tested ranking",
        })
    return Judgement(
        query_id=query.query_id,
        expert_id=profile.expert_id,
        grade=grade,
        matched_constraints=matched,
        missing_constraints=missing,
        violated_constraints=violated,
        evidence_references=sorted(set(evidence or [f"profile:{profile.expert_id}:structured_fields"])),
        rationale_codes=codes,
        rationale=rationale,
        reviewer="codex-independent-structured-audit",
        review_status="gold_reviewed" if tier == "gold" else "silver_rule_assisted",
        correction_history=correction_history,
        version="v0.4.0",
    )


def grade_map(query: BenchmarkQuery, profiles: Sequence[ExpertProfile], *, tier: str = "silver") -> dict[str, Judgement]:
    if tier == "silver":
        # Silver deliberately retains the original rule-assisted labels.  It is
        # a lower-confidence comparison tier, not an independently re-labelled
        # benchmark disguised as Gold.
        drafts = draft_judgements((query,), tuple(profiles))
        return {
            judgement.expert_id: judgement.model_copy(
                update={
                    "review_status": "silver_rule_assisted",
                    "reviewer": "rule-assisted-draft",
                    "version": "v0.4.0-silver",
                }
            )
            for judgement in drafts
        }
    return {profile.expert_id: independent_judgement(query, profile, tier=tier) for profile in profiles}


def audit_dataset(profiles: Sequence[ExpertProfile], queries: Sequence[BenchmarkQuery], judgements: Mapping[str, Judgement]) -> dict[str, Any]:
    summary_counts = Counter(judgement.grade for judgement in judgements.values())
    query_grade3 = {
        query.query_id: sum(1 for profile in profiles if independent_judgement(query, profile).grade == 3)
        for query in queries
    }
    normalized_summaries = Counter(profile.summary.lower().strip() for profile in profiles)
    templated_phrases = Counter(
        phrase for profile in profiles for phrase in ("production", "retrieval system", "hands-on delivery", "search quality")
        if phrase in profile.summary.lower()
    )
    return {
        "profile_count": len(profiles),
        "query_count": len(queries),
        "query_category_distribution": dict(Counter(query.category.value for query in queries)),
        "grade_distribution": {str(key): value for key, value in sorted(summary_counts.items())},
        "queries_with_grade_3": sum(count > 0 for count in query_grade3.values()),
        "grade_3_counts_by_query": query_grade3,
        "hard_negative_queries": sum(query.category == QueryCategory.hard_negative for query in queries),
        "employer_client_ambiguity_queries": sum("worked at" in query.query_text.lower() for query in queries),
        "delivery_mention_ambiguity_queries": sum(any(token in query.query_text.lower() for token in ("delivered", "implemented")) for query in queries),
        "temporal_queries": sum(query.category == QueryCategory.temporal for query in queries),
        "negative_constraint_queries": sum(query.category == QueryCategory.negative_constraint for query in queries),
        "duplicate_summary_count": sum(count - 1 for count in normalized_summaries.values() if count > 1),
        "near_duplicate_method": "normalized summary exact-match count; generator is highly templated",
        "templated_language_counts": dict(templated_phrases),
        "label_leakage_risk": "high: synthetic query terms and generated profile fields share a controlled vocabulary; labels are not external human ground truth",
    }


def audit_tier(
    profiles: Sequence[ExpertProfile],
    queries: Sequence[BenchmarkQuery],
    grade_maps: Mapping[str, Mapping[str, Judgement]],
) -> dict[str, Any]:
    """Aggregate dataset/judgement audit facts across an entire tier.

    ``audit_dataset`` remains useful for a single query fixture.  Gate 5 needs
    tier-level counts, so this helper prevents the report from accidentally
    describing only the first query in a tier.
    """
    all_judgements = [judgement for mapping in grade_maps.values() for judgement in mapping.values()]
    summary = audit_dataset(profiles, queries, {judgement.expert_id: judgement for judgement in all_judgements})
    summary["grade_distribution"] = dict(
        sorted((str(grade), count) for grade, count in Counter(judgement.grade for judgement in all_judgements).items())
    )
    summary["queries_with_grade_3"] = sum(
        any(judgement.grade == 3 for judgement in grade_maps.get(query.query_id, {}).values())
        for query in queries
    )
    summary["grade_3_counts_by_query"] = {
        query.query_id: sum(judgement.grade == 3 for judgement in grade_maps.get(query.query_id, {}).values())
        for query in queries
    }
    summary["review_status_counts"] = dict(
        sorted(Counter(judgement.review_status for judgement in all_judgements).items())
    )
    summary["reviewer_counts"] = dict(
        sorted(Counter(judgement.reviewer for judgement in all_judgements).items())
    )
    summary["correction_count"] = sum(bool(judgement.correction_history) for judgement in all_judgements)
    return summary


def benchmark_metrics(result_ids: Sequence[str], judgements: Mapping[str, Judgement], *, precision_k: int = 5, recall_k: int = 10) -> dict[str, float | int | None]:
    grades = {identifier: judgement.grade for identifier, judgement in judgements.items()}
    relevant = {identifier for identifier, grade in grades.items() if grade >= 1}
    relevant_grade2 = {identifier for identifier, grade in grades.items() if grade >= 2}
    relevant_grade3 = {identifier for identifier, grade in grades.items() if grade == 3}
    top_precision = list(result_ids[:precision_k])
    top_recall = list(result_ids[:recall_k])
    hits_precision = sum(grades.get(identifier, 0) > 0 for identifier in top_precision)
    hits_recall = sum(grades.get(identifier, 0) >= 1 for identifier in top_recall)
    hits_recall_grade2 = sum(grades.get(identifier, 0) >= 2 for identifier in top_recall)
    first = next((rank for rank, identifier in enumerate(top_recall, 1) if grades.get(identifier, 0) >= 1), None)
    relevance = [max(0, int(grades.get(identifier, 0))) for identifier in top_precision]
    dcg = sum((2**grade - 1) / log2(rank + 1) for rank, grade in enumerate(relevance, 1))
    ideal = sorted((max(0, int(grade)) for grade in grades.values()), reverse=True)[:precision_k]
    idcg = sum((2**grade - 1) / log2(rank + 1) for rank, grade in enumerate(ideal, 1))
    return {
        "precision_at_5": hits_precision / precision_k if precision_k else 0.0,
        "recall_at_10": hits_recall / len(relevant) if relevant else 0.0,
        "recall_at_10_grade_ge_2": hits_recall_grade2 / len(relevant_grade2) if relevant_grade2 else 0.0,
        "grade_3_hit_at_10": int(bool(relevant_grade3 & set(top_recall))),
        "judged_recall_at_10": hits_recall / len(relevant) if relevant else 0.0,
        "mrr": 1 / first if first else 0.0,
        "ndcg_at_5": dcg / idcg if idcg else 0.0,
        "grade_3_hit_rate": int(bool(relevant_grade3 & set(top_precision))),
        "hard_negative_intrusion_rate": int(any(grades.get(identifier, 0) == 0 for identifier in top_precision)),
        "required_constraint_satisfaction_rate": sum(grades.get(identifier, 0) == 3 for identifier in top_precision) / precision_k if precision_k else 0.0,
        "prohibited_constraint_violation_rate": sum(bool(judgements.get(identifier) and judgements[identifier].violated_constraints) for identifier in top_precision) / precision_k if precision_k else 0.0,
        "labelled_relevant_count": len(relevant),
        "relevant_count_grade_ge_1": len(relevant),
        "relevant_count_grade_ge_2": len(relevant_grade2),
        "grade_3_count": len(relevant_grade3),
        "no_grade_3_result": int(not relevant_grade3),
    }
