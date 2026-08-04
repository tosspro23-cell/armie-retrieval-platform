"""Reproducible query taxonomy and human-reviewable relevance judgements."""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from random import Random
from typing import Any

from pydantic import BaseModel, Field, field_validator

from armie_retrieval.datasets.models import ExpertProfile


class QueryCategory(str, Enum):
    exact_skill = "exact_skill"
    skill_industry = "skill_industry"
    delivery_project = "delivery_project"
    organization = "organization"
    seniority_role = "seniority_role"
    multi_constraint = "multi_constraint"
    semantic_paraphrase = "semantic_paraphrase"
    hard_negative = "hard_negative"
    temporal = "temporal"
    negative_constraint = "negative_constraint"


class Constraint(BaseModel):
    name: str
    value: str
    kind: str = "required"


class BenchmarkQuery(BaseModel):
    query_id: str
    query_text: str
    category: QueryCategory
    intent_summary: str
    required_constraints: list[Constraint] = Field(default_factory=list)
    optional_constraints: list[Constraint] = Field(default_factory=list)
    prohibited_constraints: list[Constraint] = Field(default_factory=list)
    expected_retrieval_signals: list[str] = Field(default_factory=list)
    judgement_set_id: str = "expert-discovery-judgements-v1"
    query_set_version: str = "v1"

    @field_validator("query_id", "query_text", "intent_summary")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query fields cannot be empty")
        return value


class Judgement(BaseModel):
    query_id: str
    expert_id: str
    grade: int
    matched_constraints: list[str] = Field(default_factory=list)
    missing_constraints: list[str] = Field(default_factory=list)
    violated_constraints: list[str] = Field(default_factory=list)
    evidence_references: list[str] = Field(default_factory=list)
    rationale_codes: list[str] = Field(default_factory=list)
    rationale: str
    reviewer: str = "rule-assisted-draft"
    review_status: str = "draft"
    correction_history: list[dict[str, Any]] = Field(default_factory=list)
    version: str = "v1"

    @field_validator("grade")
    @classmethod
    def valid_grade(cls, value: int) -> int:
        if value not in (0, 1, 2, 3):
            raise ValueError("relevance grade must be 0, 1, 2, or 3")
        return value


class JudgementSet(BaseModel):
    judgement_set_id: str
    version: str
    query_set_version: str
    judgements: list[Judgement]
    checksum: str


def _category_counts(targets: dict[QueryCategory, int] | None = None) -> dict[QueryCategory, int]:
    return targets or {
        QueryCategory.exact_skill: 15, QueryCategory.skill_industry: 15,
        QueryCategory.delivery_project: 15, QueryCategory.organization: 10,
        QueryCategory.seniority_role: 10, QueryCategory.multi_constraint: 20,
        QueryCategory.semantic_paraphrase: 15, QueryCategory.hard_negative: 10,
        QueryCategory.temporal: 5, QueryCategory.negative_constraint: 5,
    }


def generate_benchmark_queries(*, seed: int = 42, version: str = "v1", targets: dict[QueryCategory, int] | None = None) -> tuple[BenchmarkQuery, ...]:
    rng = Random(seed)
    examples: dict[QueryCategory, tuple[str, list[Constraint], list[Constraint], list[str]]] = {
        QueryCategory.exact_skill: ("Find experts with Elasticsearch experience", [Constraint(name="technology", value="Elasticsearch")], [], ["keyword", "technology"]),
        QueryCategory.skill_industry: ("Find healthcare experts with Azure AI experience", [Constraint(name="industry", value="healthcare"), Constraint(name="technology", value="Azure AI")], [], ["keyword", "metadata"]),
        QueryCategory.delivery_project: ("Find people who delivered a production RAG platform", [Constraint(name="delivery_evidence", value="project_delivery_record")], [], ["project", "delivery_evidence"]),
        QueryCategory.organization: ("Find experts who worked at Northstar Health", [Constraint(name="employer", value="Northstar Health")], [], ["employment", "organization"]),
        QueryCategory.seniority_role: ("Find senior AI Platform Leads", [Constraint(name="seniority", value="senior"), Constraint(name="role", value="AI Platform Lead")], [], ["role", "seniority"]),
        QueryCategory.multi_constraint: ("Find senior Portugal experts in energy using FAISS", [Constraint(name="seniority", value="senior"), Constraint(name="location", value="Portugal"), Constraint(name="industry", value="energy"), Constraint(name="technology", value="FAISS")], [], ["metadata", "dense", "keyword"]),
        QueryCategory.semantic_paraphrase: ("Locate practitioners who built meaning-aware search", [Constraint(name="technology", value="semantic search")], [], ["dense", "paraphrase"]),
        QueryCategory.hard_negative: ("Find delivery leaders who implemented Elasticsearch", [Constraint(name="delivery_evidence", value="project_delivery_record"), Constraint(name="technology", value="Elasticsearch")], [Constraint(name="summary_only", value="true", kind="prohibited")], ["hard_negative", "project"]),
        QueryCategory.temporal: ("Find experts with recent retrieval delivery", [Constraint(name="delivery_year", value="2022")], [], ["date", "project"]),
        QueryCategory.negative_constraint: ("Find experts outside financial services using RAG", [Constraint(name="technology", value="RAG")], [Constraint(name="industry", value="financial services", kind="prohibited")], ["negative_filter", "metadata"]),
    }
    records: list[BenchmarkQuery] = []
    for category, count in _category_counts(targets).items():
        base_text, required, prohibited, signals = examples[category]
        for index in range(count):
            suffix = "" if index == 0 else f" (case {index + 1})"
            records.append(BenchmarkQuery(
                query_id=f"q-{category.value}-{index + 1:03d}", query_text=base_text + suffix,
                category=category, intent_summary=base_text, required_constraints=required,
                prohibited_constraints=prohibited, expected_retrieval_signals=signals,
                query_set_version=version,
            ))
    rng.shuffle(records)
    return tuple(sorted(records, key=lambda query: query.query_id))


def validate_judgements(queries: list[BenchmarkQuery] | tuple[BenchmarkQuery, ...], judgements: list[Judgement] | tuple[Judgement, ...]) -> None:
    query_ids = {query.query_id for query in queries}
    if not query_ids:
        raise ValueError("query set cannot be empty")
    for judgement in judgements:
        if judgement.query_id not in query_ids:
            raise ValueError(f"judgement references unknown query: {judgement.query_id}")
        if not judgement.expert_id.strip():
            raise ValueError("judgement expert_id cannot be empty")
    if len({query.category for query in queries}) < 5:
        raise ValueError("query taxonomy coverage is insufficient")


def judgement_checksum(judgements: list[Judgement] | tuple[Judgement, ...]) -> str:
    payload = [judgement.model_dump(mode="json") for judgement in judgements]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def draft_judgements(queries: list[BenchmarkQuery] | tuple[BenchmarkQuery, ...], profiles: list[ExpertProfile] | tuple[ExpertProfile, ...]) -> tuple[Judgement, ...]:
    """Create transparent rule-assisted drafts; these are not a substitute for review."""
    drafts: list[Judgement] = []
    for query in queries:
        for profile in profiles:
            matched: list[str] = []
            missing: list[str] = []
            violated: list[str] = []
            for constraint in query.required_constraints:
                haystack = json.dumps(profile.search_document, sort_keys=True).lower()
                (matched if constraint.value.lower() in haystack else missing).append(f"{constraint.name}={constraint.value}")
            for constraint in query.prohibited_constraints:
                if constraint.value.lower() in json.dumps(profile.search_document, sort_keys=True).lower():
                    violated.append(f"{constraint.name}={constraint.value}")
            if violated:
                grade, rationale = 0, "prohibited constraint present"
            elif not matched:
                grade, rationale = 0, "no required constraint evidence"
            elif len(missing) == 0 and len(matched) >= max(1, len(query.required_constraints)):
                grade, rationale = 3, "all required constraints have generated project or structured evidence"
            else:
                grade, rationale = 1, "partial constraint evidence"
            drafts.append(Judgement(
                query_id=query.query_id, expert_id=profile.expert_id, grade=grade,
                matched_constraints=matched, missing_constraints=missing,
                violated_constraints=violated, evidence_references=[profile.projects[0].project_id] if profile.projects else [],
                rationale_codes=["rule_assisted_draft"], rationale=rationale,
            ))
    return tuple(drafts)
