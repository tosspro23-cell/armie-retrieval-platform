"""Stable domain contracts exchanged between platform components."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any, Mapping
from uuid import uuid4


@dataclass(frozen=True)
class Query:
    text: str
    domain: str = "expert_discovery"
    filters: Mapping[str, Any] = field(default_factory=dict)
    top_k: int = 5
    request_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class RetrievalPlan:
    """Declarative intent. It must not contain provider or SDK details."""

    strategy: str
    processor_names: tuple[str, ...] = ()
    top_k: int = 5
    filters: Mapping[str, Any] = field(default_factory=dict)
    constraints: Mapping[str, Any] = field(default_factory=dict)
    parameters: Mapping[str, Any] = field(default_factory=dict)
    plan_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class ResultItem:
    id: str
    object_type: str
    title: str
    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    score: float = 0.0
    sources: tuple[str, ...] = ()
    signals: Mapping[str, float] = field(default_factory=dict)

    def with_score(self, score: float, *, signals: Mapping[str, float] | None = None) -> "ResultItem":
        return ResultItem(
            id=self.id, object_type=self.object_type, title=self.title, content=self.content,
            metadata=self.metadata, score=score, sources=self.sources,
            signals=self.signals if signals is None else signals,
        )


@dataclass(frozen=True)
class RetrievalResult:
    items: tuple[ResultItem, ...]
    plan_id: str
    strategy: str
    latency_ms: float
    provenance: Mapping[str, Any] = field(default_factory=dict)
    trace: tuple[str, ...] = ()
    created_at: float = field(default_factory=time)

    def with_items(self, items: tuple[ResultItem, ...], trace_entry: str) -> "RetrievalResult":
        return RetrievalResult(
            items=items, plan_id=self.plan_id, strategy=self.strategy,
            latency_ms=self.latency_ms, provenance=self.provenance,
            trace=(*self.trace, trace_entry), created_at=self.created_at,
        )


@dataclass(frozen=True)
class EvaluationResult:
    """Observational quality metrics. Evaluation must not mutate a runtime result."""

    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float
    latency_ms: float
    result_count: int


@dataclass(frozen=True)
class ExecutionObservation:
    """Immutable runtime event consumed by offline learning only."""

    component_type: str
    component_name: str
    event_type: str
    details: Mapping[str, Any] = field(default_factory=dict)
    plan_id: str | None = None
    observation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: float = field(default_factory=time)


@dataclass(frozen=True)
class Policy:
    """Versioned, published runtime guidance produced offline from observations."""

    version: int
    planner_defaults: Mapping[str, Any] = field(default_factory=dict)
    retriever_priority: Mapping[str, int] = field(default_factory=dict)
    processor_defaults: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()
    published_at: float = field(default_factory=time)
