"""Structured, presentation-independent retrieval observability contracts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Mapping


def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


@dataclass(frozen=True)
class CandidateTrace:
    expert_id: str
    title: str
    retriever: str
    rank: int
    raw_score: float
    normalized_score: float
    matched_terms: tuple[str, ...] = ()
    matched_fields: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    scoring_components: Mapping[str, float] = field(default_factory=dict)
    contributions: Mapping[str, Mapping[str, float]] = field(default_factory=dict)
    final_score: float | None = None
    final_rank: int | None = None
    relevant: bool | None = None
    expected_constraints: tuple[str, ...] = ()
    matched_constraints: tuple[str, ...] = ()
    missing_constraints: tuple[str, ...] = ()
    constraint_coverage_ratio: float | None = None
    matched_graph_nodes: tuple[str, ...] = ()
    matched_graph_edges: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlannerTrace:
    raw_query: str
    provider: str
    model: str | None
    raw_output: Mapping[str, Any] | None
    parsed_plan: Mapping[str, Any]
    selected_strategy: str
    selected_retrievers: tuple[str, ...]
    extracted_entities: tuple[str, ...] = ()
    extracted_skills: tuple[str, ...] = ()
    extracted_industries: tuple[str, ...] = ()
    extracted_organizations: tuple[str, ...] = ()
    filters: Mapping[str, Any] = field(default_factory=dict)
    constraints: Mapping[str, Any] = field(default_factory=dict)
    requested_top_k: int = 0
    query_rewrite: str | None = None
    fallback: str | None = None
    warnings: tuple[str, ...] = ()
    latency_ms: float = 0.0
    requested_provider: str | None = None
    actual_provider: str | None = None
    requested_model: str | None = None
    fallback_enabled: bool = False
    fallback_reason: str | None = None
    reason_codes: tuple[str, ...] = ()
    constraint_types: tuple[str, ...] = ()
    requested_retrievers: tuple[str, ...] = ()
    available_capabilities: Mapping[str, str] = field(default_factory=dict)
    planner_requested_top_k: int = 0
    retrieval_candidate_k: int = 0
    rerank_candidate_k: int = 0
    effective_final_top_k: int = 0
    effective_top_k_source: str = "default"
    fallback_diagnostic: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class RetrieverTrace:
    name: str
    strategy: str
    latency_ms: float
    candidate_count_before_truncation: int
    candidate_limit: int
    candidates: tuple[CandidateTrace, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class FusionTrace:
    method: str
    candidates: tuple[CandidateTrace, ...]
    deduplicated_ids: tuple[str, ...] = ()
    rrf_k: int | None = None
    tie_breaking: str = "stable input order after descending score"


@dataclass(frozen=True)
class RankingTrace:
    candidates: tuple[CandidateTrace, ...]
    processors: tuple[str, ...]
    tie_breaking: str = "stable input order after descending score"


@dataclass(frozen=True)
class ProcessorStageTrace:
    processor_name: str
    candidate_count_before: int
    candidate_count_after: int
    order_before: tuple[str, ...]
    order_after: tuple[str, ...]
    scores_before: Mapping[str, float]
    scores_after: Mapping[str, float]
    removed_ids: tuple[str, ...] = ()
    rank_changes: Mapping[str, int] = field(default_factory=dict)
    changed_scores: bool = False
    changed_order: bool = False
    truncated: bool = False


@dataclass(frozen=True)
class RerankerTrace:
    requested_provider: str
    actual_provider: str
    model: str | None
    candidate_count_in: int
    candidate_count_after_rerank: int
    final_candidate_count: int
    candidates: tuple[Mapping[str, Any], ...] = ()
    model_available: bool = True
    fallback_reason: str | None = None
    device: str | None = None
    batch_size: int | None = None
    model_load_latency_ms: float = 0.0
    inference_latency_ms: float = 0.0
    warnings: tuple[str, ...] = ()
    post_rerank_top_k: int = 0
    final_processor_output_count: int = 0
    fusion_output_candidates: int = 0
    rerank_input_candidates: int = 0
    reranker_processed_candidates: int = 0
    post_rerank_candidates: int = 0
    final_top_k_candidates: int = 0
    scoring_method: str = "none"
    fallback_diagnostic: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class GroundTruthTrace:
    query_id: str
    relevant_ids: tuple[str, ...]
    retrieved_ids: tuple[str, ...]
    relevant_retrieved_ids: tuple[str, ...]
    missed_relevant_ids: tuple[str, ...]
    non_relevant_ids: tuple[str, ...]
    first_relevant_rank: int | None


@dataclass(frozen=True)
class EvaluationTrace:
    metrics: Mapping[str, float]
    calculation: Mapping[str, Any]


@dataclass(frozen=True)
class RetrievalTrace:
    schema_version: str
    query_id: str
    planner: PlannerTrace
    retrievers: tuple[RetrieverTrace, ...]
    fusion: FusionTrace | None
    ranking: RankingTrace
    ground_truth: GroundTruthTrace | None
    evaluation: EvaluationTrace | None
    timing_ms: Mapping[str, float]
    warnings: tuple[str, ...] = ()
    processor_stages: tuple[ProcessorStageTrace, ...] = ()
    reranking: RerankerTrace | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, default=_json_default)

    @classmethod
    def from_json(cls, payload: str) -> Mapping[str, Any]:
        """Return a JSON-compatible trace mapping for lossless export round-trip checks."""
        return json.loads(payload)
