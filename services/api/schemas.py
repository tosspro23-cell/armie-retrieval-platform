from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: str | None = None
    profile: str = "H2"
    query_case_id: str | None = None
    benchmark_query_id: str | None = None

class StructuredQueryRequest(BaseModel):
    """Trusted structured v0.5 contract; no natural-language extraction."""
    query: str = Field(min_length=1)
    contract: dict[str, Any] = Field(default_factory=dict)
    requested_k: int = Field(default=5, ge=1, le=100)

class SessionRequest(BaseModel):
    pass

class QueryLabRunRequest(BaseModel):
    case_id: str
    profile: str = "baseline"

class BenchmarkRunRequest(BaseModel):
    query_id: str
    profile: str = "H2"

class CompareRequest(BaseModel):
    left_run_id: str
    right_run_id: str

class StageSummary(BaseModel):
    model_config = ConfigDict(extra="allow")
    stage: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)
    summary: dict[str, Any] = Field(default_factory=dict)

class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    evidence_id: str
    result_id: str
    title: str = ""
    snippet: str = ""

class VerificationFinding(BaseModel):
    model_config = ConfigDict(extra="allow")
    rule_id: str
    name: str
    description: str
    status: str
    expected: Any = None
    actual: Any = None
    related_result_ids: list[str] = Field(default_factory=list)
    related_evidence_ids: list[str] = Field(default_factory=list)

class VerificationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str
    findings: list[VerificationFinding] = Field(default_factory=list)
    labelled: bool = False

class WorkbenchResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    schema_version: str
    request_id: str
    trace_id: str
    session_id: str
    profile: str
    query: dict[str, Any]
    plan: dict[str, Any]
    answer_summary: dict[str, Any]
    results: list[dict[str, Any]]
    evidence: list[EvidenceItem]
    evidence_by_result: dict[str, Any] = Field(default_factory=dict)
    verification: VerificationResponse
    metrics: dict[str, Any]
    stage_summaries: list[StageSummary]
    execution: dict[str, Any] = Field(default_factory=dict)
    execution_context: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    fallbacks: list[str] = Field(default_factory=list)
    raw_trace: dict[str, Any] = Field(default_factory=dict)
    repeatability: dict[str, Any] = Field(default_factory=dict)
    trace_url: str = ""

class ComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    left_run_id: str
    right_run_id: str
    left: dict[str, Any]
    right: dict[str, Any]
    overlap: dict[str, Any] = Field(default_factory=dict)
    rank_delta: list[dict[str, Any]] = Field(default_factory=list)
    metric_delta: dict[str, Any] = Field(default_factory=dict)

class ApiResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    schema_version: str = "0.5.0"

class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}

class ErrorEnvelope(BaseModel):
    error: ErrorBody
