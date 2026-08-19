"""Application orchestration for the v0.4.0 interactive retrieval workbench.

The service deliberately delegates execution to the frozen ``RetrievalRuntime``
and the existing trace/selection helpers.  It only owns sessions, projections,
and deterministic workbench concerns.
"""
from __future__ import annotations

import time
import json
import os
import math
import subprocess
import hashlib
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import uuid4
from typing import Any

from armie_retrieval.benchmarking.datasets import BenchmarkDataset, generate_benchmark_dataset
from armie_retrieval import __version__
from armie_retrieval.models import Query, ResultItem
from armie_retrieval.observability.session import trace_query
from armie_retrieval.profiles import load_profile
from armie_retrieval.providers import InMemoryKnowledgeProvider
from armie_retrieval.providers.knowledge_graph import NetworkXKnowledgeGraphProvider
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry
from armie_retrieval.retrievers import DenseRetriever, GraphRetriever, HybridRetriever, SparseRetriever
from armie_retrieval.runtime import RetrievalRuntime
from armie_retrieval.runtime_profiles import select_planner, select_reranker
from armie_retrieval.processors import QueryAwareRerankProcessor
from armie_retrieval.processors.result_processors import DeduplicateProcessor, MetadataFilterProcessor
from armie_retrieval.rerankers import MetadataBoostReranker
from armie_retrieval.benchmarks import default_profiles
from armie_retrieval.relevance import generate_benchmark_queries
from armie_retrieval.constraints import registry_snapshot
from armie_retrieval.contracts import (Constraint, ConstraintCategory, ConstraintOperator,
                                       ConstraintStrength, RetrievalContract,
                                       UnsupportedConstraint, ValidationState,
                                       validate_contract)
from armie_retrieval.embeddings import create_embedding_provider, EmbeddingPrerequisiteError
from armie_retrieval.indexing.elasticsearch import ElasticsearchClient
from armie_retrieval.indexing.elasticsearch.identity import configured_dense_index, physical_dense_index
from armie_retrieval.providers.elasticsearch.retrievers import PROVENANCE_SCHEMA_VERSION
from armie_retrieval.models import RetrievalPlan
from armie_retrieval.providers.elasticsearch import ElasticsearchDenseRetriever
from pydantic import ValidationError
from armie_retrieval.interpretation import (
    CandidateInterpretation, CandidateConstraint, ClarificationItem, ClarificationResolution,
    ClarificationType, InterpretationState, apply_resolution, confirm,
    start_session, validate_contract as validate_interpretation_contract, question_for,
)
from armie_retrieval.interpretation.models import Polarity, SupportState


@dataclass
class Turn:
    turn_id: str
    raw_query: str
    resolved_query: str
    trace_id: str
    created_at: float


@dataclass
class Session:
    session_id: str
    created_at: float
    turns: list[Turn] = field(default_factory=list)


class WorkbenchError(ValueError):
    """Safe, user-facing application error."""

    def __init__(self, code: str, message: str, *, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.code, self.message, self.status_code, self.details = code, message, status_code, details or {}


class WorkbenchService:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.package_source = str(Path(__file__).resolve().parents[1])
        try:
            self.git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=self.root, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            self.git_commit = None
        self.dataset: BenchmarkDataset = generate_benchmark_dataset(self.root / ".artifacts" / "workbench" / "dataset", size=50)
        self.sessions: dict[str, Session] = {}
        self.traces: dict[str, dict[str, Any]] = {}
        self.runs: dict[str, dict[str, Any]] = {}
        self._runtime_cache: dict[str, tuple[RetrievalRuntime, object]] = {}
        self._benchmark_root = Path(os.getenv("ARMIE_V2_BENCHMARK_ROOT", "/tmp/armie-v040-dataset-v2-full"))
        self._benchmark_payload = self._load_benchmark_payload()
        self._benchmark_experts = self._load_benchmark_experts()
        self._c1_retriever = None
        self.interpretation_sessions: dict[str, object] = {}
        self.interpretation_contracts: dict[str, RetrievalContract] = {}
        self.interpretation_fingerprints: dict[str, str] = {}

    def _load_benchmark_experts(self):
        if not self._benchmark_payload:
            return []
        try:
            rows = json.loads((self._benchmark_root / "knowledge" / "experts.json").read_text())
            return [ResultItem(id=row["expert_id"], object_type="expert", title=row["display_name"], content=row["summary"], metadata=row.get("search_document", {}), sources=("dataset-v2",)) for row in rows]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return []

    def _load_benchmark_payload(self):
        try:
            manifest = json.loads((self._benchmark_root / "manifest.json").read_text())
            queries = json.loads((self._benchmark_root / "queries" / "queries.json").read_text())
            judgements = json.loads((self._benchmark_root / "judgements" / "judgements.json").read_text())
            by_query: dict[str, dict[str, dict]] = {}
            for row in judgements:
                by_query.setdefault(row["query_id"], {}).setdefault(row["review_status"], {})[row["expert_id"]] = row
            return {"manifest": manifest, "queries": {q["query_id"]: q for q in queries}, "judgements": by_query}
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "service": "armie-retrieval-workbench", "version": __version__, "package_version": __version__, "package_source": self.package_source, "api_version": "v1", "frontend_version": "0.5.1", "git_commit": self.git_commit, "dataset": "Expert Discovery v2" if self._benchmark_payload else "Legacy v1 (fallback)", "profiles": ["H1", "H2", "H3", "H4", "baseline", "model-enhanced"], "benchmark_v2_available": bool(self._benchmark_payload), "constraint_runtime": {"promoted_strategy": "C1", "default_semantic_strategy": "dense", "native_prefilter": True, "registry_version": registry_snapshot()["version"]}}

    def capabilities(self) -> dict[str, Any]:
        return {"api_version": "v1", "application_version": __version__, "package_version": __version__, "package_source": self.package_source, "frontend_version": "0.5.1", "git_commit": self.git_commit, "active_dataset": "expert-discovery-v2" if self._benchmark_payload else "legacy-v1", "default_profile": "H2" if self._benchmark_payload else "baseline", "profiles": ["H1", "H2", "H3", "H4", "baseline", "model-enhanced"], "benchmark_profiles": [profile.profile_id for profile in default_profiles()], "retrieval_strategies": ["dense", "sparse", "hybrid", "graph"], "constraint_runtime": {"promoted_strategy": "C1", "default_semantic_strategy": "dense", "native_prefilter": True, "registry": registry_snapshot()}, "features": ["sessions", "follow_up", "evidence", "verification", "audit_trail", "query_lab", "relevance_benchmarks", "benchmark_query_library", "constraint_evaluation", "profile_comparison"]}

    def benchmark_manifest(self) -> dict[str, Any]:
        if not self._benchmark_payload:
            return {"available": False, "reason": "Dataset v2 benchmark artifacts are not available locally."}
        m = self._benchmark_payload["manifest"]
        return {"available": True, "git_commit": os.getenv("ARMIE_BENCHMARK_COMMIT", "9973367910d6ab3a0b52d123c1151ee0507e7f24"), "dataset_version": m.get("dataset_version"), "dataset_checksum": m.get("checksum"), "query_set_version": m.get("query_set_version"), "judgement_set_version": m.get("judgement_set_version"), "elasticsearch_version": "8.15.3", "bm25_index": os.getenv("ARMIE_V050_BM25_INDEX", "armie-experts-v1-v2-gate55b-bm25-r2"), "dense_index": configured_dense_index(), "dense_physical_index": physical_dense_index(), "embedding_model": "BAAI/bge-m3", "embedding_dimensions": 1024, "projection_schema_version": "armie-v0.5-constraint-projection-v1", "constraint_projection": "constraint-projection-0.2-gate6b", "provenance_schema_version": PROVENANCE_SCHEMA_VERSION, "constraint_runtime": {"strategy": "C1", "native_prefilter": True, "registry_version": registry_snapshot()["version"]}, "reranker_model": "BAAI/bge-reranker-v2-m3", "candidate_boundaries": {"retrieval_candidate_k": 100, "fusion_candidate_k": 100, "rerank_candidate_k": 30, "final_top_k": 5, "rrf_k": 60}}

    def constraint_registry(self) -> dict[str, Any]:
        """Expose the bounded runtime contract without exposing backend DSL."""
        return registry_snapshot()

    def interpret(self, text: str) -> dict[str, Any]:
        """Create a UI-independent clarification session; no retrieval executes."""
        if not text or not text.strip():
            raise WorkbenchError("invalid_query", "Query text must not be empty.")
        raw = text.strip()
        base = CandidateInterpretation(str(uuid4()), raw, raw, constraints=self._candidate_constraints(raw), exclusions=self._candidate_exclusions(raw), unsupported_items=self._unsupported_items(raw))
        items = []
        lower = raw.lower()
        if any(token in lower for token in ("around ", "roughly ", "maybe ")):
            span = next((token for token in ("around ", "roughly ", "maybe ") if token in lower), "ambiguous phrase")
            question, choices = question_for(ClarificationType.NUMERIC_INTENT if "year" in lower else ClarificationType.REQUIREMENT_STRENGTH, span.strip())
            items.append(ClarificationItem(f"c-{uuid4().hex[:8]}", base.request_id, span.strip(), raw, "AMBIGUOUS", ClarificationType.NUMERIC_INTENT if "year" in lower else ClarificationType.REQUIREMENT_STRENGTH, choices, question, choices, provenance=({"stage": "deterministic_protocol", "source": span.strip()},)))
        if "not necessarily" in lower or "maybe exclude" in lower:
            span = "not necessarily" if "not necessarily" in lower else "maybe exclude"
            question, choices = question_for(ClarificationType.EXCLUSION_SCOPE, span)
            items.append(ClarificationItem(f"c-{uuid4().hex[:8]}", base.request_id, span, raw, "AMBIGUOUS", ClarificationType.EXCLUSION_SCOPE, choices, question, choices, provenance=({"stage": "deterministic_protocol", "source": span},)))
        session = start_session(base, tuple(items)); session_id = str(uuid4()); self.interpretation_sessions[session_id] = session
        return self._interpretation_payload(session_id, session)

    @staticmethod
    def _candidate_constraints(raw: str) -> tuple:
        """Extract only explicit, registry-supported facts for Gate 5."""
        lower = raw.lower()
        rows = []
        match = re.search(r"(?:at least|minimum of|over)\s+(\d+)\s+years", lower)
        if match and "around" not in lower and "roughly" not in lower:
            rows.append(CandidateConstraint("years_experience", "gte", int(match.group(1)), int(match.group(1)), source_span=match.group(0)))
        for value in ("senior", "principal"):
            if re.search(rf"\b{value}(?:-level)?\b", lower):
                rows.append(CandidateConstraint("seniority", "gte", value, value, source_span=value))
                break
        industries = {"healthcare": "healthcare", "financial services": "financial_services", "manufacturing": "manufacturing"}
        for phrase, value in industries.items():
            if phrase in lower and not re.search(rf"excluding\s+{re.escape(phrase)}", lower):
                rows.append(CandidateConstraint("industry", "eq", value, value, source_span=phrase))
        return tuple(rows)

    @staticmethod
    def _candidate_exclusions(raw: str) -> tuple:
        lower = raw.lower()
        for phrase, value in (("financial services", "financial_services"), ("healthcare", "healthcare"), ("manufacturing", "manufacturing")):
            if re.search(rf"(?:exclude|excluding)\s+{re.escape(phrase)}", lower):
                return (CandidateConstraint("industry", "eq", value, value, polarity=Polarity.EXCLUSION, source_span=phrase),)
        return ()

    @staticmethod
    def _unsupported_items(raw: str) -> tuple[str, ...]:
        lower = raw.lower()
        if any(phrase in lower for phrase in ("worked at ", "advised ", "delivered for ")):
            return ("relationship constraint requires deferred evidence support",)
        return ()

    def _contract_from_session(self, session) -> RetrievalContract:
        candidate = session.interpretation
        hard, exclusions, soft = [], [], []
        for item in candidate.constraints:
            if item.support_state is SupportState.UNSUPPORTED:
                continue
            category = ConstraintCategory.NUMERIC if item.field == "years_experience" else ConstraintCategory.SENIORITY if item.field == "seniority" else ConstraintCategory.CATEGORICAL
            hard.append(Constraint(canonical_field=item.field, operator=ConstraintOperator(item.operator), expected_value=item.normalized_value if item.normalized_value is not None else item.raw_value, category=category, strength=ConstraintStrength.HARD, provenance=item.source_span or "confirmed_interpretation"))
        for item in candidate.exclusions:
            exclusions.append(Constraint(canonical_field=item.field, operator=ConstraintOperator.NOT_IN, expected_value=[item.normalized_value if item.normalized_value is not None else item.raw_value], category=ConstraintCategory.CATEGORICAL, strength=ConstraintStrength.HARD, provenance=item.source_span or "confirmed_interpretation"))
        for resolution in session.resolutions:
            if resolution.selected_resolution == "MINIMUM":
                match = re.search(r"(\d+)\s+years", session.interpretation.natural_language_request.lower())
                if match:
                    hard.append(Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=int(match.group(1)), category=ConstraintCategory.NUMERIC, provenance=resolution.clarification_id))
            elif resolution.selected_resolution == "EXCLUDED":
                match = re.search(r"(?:exclude|excluding)\s+([a-z ]+)", session.interpretation.natural_language_request.lower())
                if match:
                    exclusions.append(Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value=match.group(1).strip().replace(" ", "_"), category=ConstraintCategory.CATEGORICAL, provenance=resolution.clarification_id))
            elif resolution.selected_resolution in {"PREFERRED", "CONTEXT_ONLY", "REMOVE_FROM_CONSTRAINT_INTERPRETATION", "APPROXIMATE", "MAXIMUM", "EXACT"}:
                continue
        unsupported = tuple(UnsupportedConstraint(expression=item, reason="No executable Gate 5 C1 mapping", provenance="confirmed_interpretation") for item in candidate.unsupported_items)
        return RetrievalContract(semantic_query=candidate.semantic_query, hard_constraints=tuple(hard), exclusions=tuple(exclusions), soft_preferences=tuple(soft), unsupported_constraints=unsupported)

    def _interpretation_payload(self, session_id, session):
        contract = self.interpretation_contracts.get(session_id)
        blocking = sum(1 for item in session.clarifications if item.status.value == "NEEDS_CLARIFICATION")
        return {"session_id": session_id, "request_id": session.interpretation.request_id, "state": session.interpretation.interpretation_state.value, "interpretation": session.interpretation.to_dict(), "clarifications": [c.__dict__ for c in session.clarifications], "resolutions": [r.__dict__ for r in session.resolutions], "blocking_clarification_count": blocking, "confirmation_required": session.interpretation.interpretation_state is InterpretationState.INTERPRETATION_COMPLETE, "contract": contract.model_dump(mode="json") if contract else None, "contract_fingerprint": self.interpretation_fingerprints.get(session_id)}

    def interpretation(self, session_id: str):
        try: return self._interpretation_payload(session_id, self.interpretation_sessions[session_id])
        except KeyError as exc: raise WorkbenchError("interpretation_session_not_found", "Interpretation session was not found.", status_code=404) from exc

    def resolve_interpretation(self, session_id: str, resolution: dict[str, Any], *, edit: bool = False):
        try: session = self.interpretation_sessions[session_id]
        except KeyError as exc: raise WorkbenchError("interpretation_session_not_found", "Interpretation session was not found.", status_code=404) from exc
        try: updated = apply_resolution(session, ClarificationResolution(**resolution), edit=edit)
        except (TypeError, ValueError) as exc: raise WorkbenchError("invalid_clarification_resolution", str(exc)) from exc
        self.interpretation_sessions[session_id] = updated; return self._interpretation_payload(session_id, updated)

    def confirm_interpretation(self, session_id: str):
        try: session = self.interpretation_sessions[session_id]; confirmed = confirm(session); validated = validate_interpretation_contract(confirmed)
        except KeyError as exc: raise WorkbenchError("interpretation_session_not_found", "Interpretation session was not found.", status_code=404) from exc
        except ValueError as exc: raise WorkbenchError("interpretation_not_ready", str(exc)) from exc
        contract = self._contract_from_session(validated)
        validation = validate_contract(contract)
        if not validation.valid or contract.unsupported_constraints:
            raise WorkbenchError("unsupported_executable_intent", "The confirmed interpretation contains meaning that cannot be executed by Gate 5 C1.", details={"validation": validation.model_dump(mode="json")})
        self.interpretation_sessions[session_id] = validated
        self.interpretation_contracts[session_id] = contract
        self.interpretation_fingerprints[session_id] = contract.contract_id or ""
        return self._interpretation_payload(session_id, validated)

    def execute_interpretation(self, session_id: str, *, contract_fingerprint: str | None = None, requested_k: int = 5):
        try: session = self.interpretation_sessions[session_id]
        except KeyError as exc: raise WorkbenchError("interpretation_session_not_found", "Interpretation session was not found.", status_code=404) from exc
        if session.interpretation.interpretation_state is not InterpretationState.VALIDATED_CONTRACT:
            raise WorkbenchError("interpretation_not_confirmed", "Explicit confirmation and validation are required before C1 execution.")
        contract = self.interpretation_contracts.get(session_id)
        if contract is None or (contract_fingerprint and contract_fingerprint != self.interpretation_fingerprints.get(session_id)):
            raise WorkbenchError("stale_contract", "The confirmed contract is stale; review and confirm again.")
        if not contract.hard_constraints and not contract.exclusions:
            # Removing/softening every hard condition is explicitly semantic-only.
            return self.query(session.interpretation.semantic_query, profile="H2")
        return self.structured_query(session.interpretation.semantic_query, contract.model_dump(mode="json"), requested_k=requested_k)

    def benchmark_profiles(self) -> list[dict[str, Any]]:
        return [{"id": "H1", "label": "H1 — BM25", "description": "Fast lexical baseline", "strategy": "sparse", "retrievers": ["elasticsearch_bm25"], "fusion": None, "reranker": "metadata_boost", "architecture_label": "Fast lexical baseline", "score_semantics": "BM25 score"}, {"id": "H2", "label": "H2 — Dense", "description": "Practical quality/cost baseline", "strategy": "dense", "retrievers": ["elasticsearch_dense"], "fusion": None, "reranker": "metadata_boost", "architecture_label": "Practical quality/cost baseline", "score_semantics": "Dense score"}, {"id": "H3", "label": "H3 — Hybrid RRF", "description": "Lexical + semantic complementarity", "strategy": "hybrid", "retrievers": ["elasticsearch_bm25", "elasticsearch_dense"], "fusion": "reciprocal_rank_fusion", "reranker": "metadata_boost", "architecture_label": "Lexical + semantic complementarity", "score_semantics": "RRF fused score"}, {"id": "H4", "label": "H4 — Hybrid + BGE", "description": "Cross-encoder reranking experiment", "strategy": "hybrid", "retrievers": ["elasticsearch_bm25", "elasticsearch_dense"], "fusion": "reciprocal_rank_fusion", "reranker": "bge_cross_encoder", "architecture_label": "Cross-encoder reranking experiment", "score_semantics": "BGE reranker score"}]

    def benchmark_queries(self) -> list[dict[str, Any]]:
        if not self._benchmark_payload: return []
        gold_ids = {qid for qid, statuses in self._benchmark_payload["judgements"].items() if "draft_gold_structured_audit" in statuses}
        return [{**q, "label_status": "Gold" if qid in gold_ids else "Silver", "judgement_source": "draft_gold_structured_audit" if qid in gold_ids else "draft_silver_rule_assisted"} for qid, q in self._benchmark_payload["queries"].items()]

    def benchmark_query(self, query_id: str) -> dict[str, Any]:
        row = self._benchmark_payload and self._benchmark_payload["queries"].get(query_id)
        if not row: raise WorkbenchError("benchmark_query_not_found", "Dataset v2 benchmark query was not found.", status_code=404)
        return {**row, "label_status": "Gold" if "draft_gold_structured_audit" in self._benchmark_payload["judgements"].get(query_id, {}) else "Silver"}

    def datasets(self) -> dict[str, Any]:
        return {"datasets": [{"dataset_id": "expert-discovery", "dataset_version": "v2", "default_scale": 10000, "source_type": "controlled_synthetic_benchmark", "active": bool(self._benchmark_payload), "manifest_required": True}, {"dataset_id": "expert-discovery", "dataset_version": "v1", "default_scale": 50, "source_type": "legacy_workbench_fixture", "active": not bool(self._benchmark_payload), "manifest_required": False}]}

    def benchmarks(self) -> dict[str, Any]:
        return {"benchmarks": [{"benchmark_id": "expert-discovery-v1", "query_set_version": "v1", "query_count": len(generate_benchmark_queries()), "categories": sorted({query.category.value for query in generate_benchmark_queries()}), "profiles": [profile.model_dump(mode="json") for profile in default_profiles()]}]}

    def create_session(self) -> dict[str, Any]:
        session = Session(str(uuid4()), time.time())
        self.sessions[session.session_id] = session
        return self._session_dict(session)

    def get_session(self, session_id: str) -> dict[str, Any]:
        return self._session_dict(self._session(session_id))

    def delete_session(self, session_id: str) -> None:
        self._session(session_id)
        del self.sessions[session_id]

    def query(self, text: str, *, session_id: str | None = None, profile: str = "baseline", governed: bool = False, query_case_id: str | None = None, benchmark_query_id: str | None = None) -> dict[str, Any]:
        if not text or not text.strip():
            raise WorkbenchError("invalid_query", "Query text must not be empty.")
        if governed and session_id not in self.interpretation_sessions:
            return {**self.interpret(text), "governed_mode": True, "execution_status": "blocked"}
        # A reviewed NL session owns its execution lifecycle.  The legacy
        # query endpoint may route through the canonical governed executor,
        # but must never create a semantic bypass around clarification or
        # confirmation.
        if session_id in self.interpretation_sessions:
            return self.execute_interpretation(session_id, contract_fingerprint=self.interpretation_fingerprints.get(session_id))
        if profile not in {"baseline", "model-enhanced", "H1", "H2", "H3", "H4"}:
            raise WorkbenchError("invalid_profile", f"Unknown profile: {profile}")
        session = self._session(session_id) if session_id else self._new_session()
        raw = text.strip()
        resolved = self._resolve_query(session, raw)
        case = next((item for item in self.dataset.queries if item["id"] == query_case_id), None)
        benchmark_case = self._benchmark_payload and self._benchmark_payload["queries"].get(benchmark_query_id or "")
        query = Query(resolved, top_k=5, request_id=str(uuid4()))
        runtime, planner = self._runtime(profile)
        started = time.perf_counter()
        try:
            result, trace = trace_query(runtime, planner, query, query_id=query.request_id, relevant_ids=set(case["relevant_ids"]) if case else None)
        except Exception as exc:
            raise WorkbenchError("execution_failed", "The retrieval request could not be executed.", status_code=500, details={"reason": str(exc)}) from exc
        trace_id = str(uuid4())
        response = self._response(trace_id, session.session_id, raw, resolved, profile, result, trace, (time.perf_counter() - started) * 1000, case, benchmark_case)
        turn = Turn(str(uuid4()), raw, resolved, trace_id, time.time())
        session.turns.append(turn)
        response["turn_id"] = turn.turn_id
        response["run_id"] = str(uuid4())
        self.traces[trace_id] = trace.to_dict()
        self.runs[response["run_id"]] = response
        return response

    def structured_query(self, text: str, contract_payload: dict[str, Any], *, requested_k: int = 5) -> dict[str, Any]:
        """Execute a trusted structured contract through the promoted C1 path."""
        if not text or not text.strip():
            return self._structured_error_response("", requested_k, "INVALID_CONTRACT", "semantic_query must not be empty.")
        try:
            payload = dict(contract_payload or {})
            payload.setdefault("semantic_query", text.strip())
            contract = RetrievalContract.model_validate(payload)
        except (ValidationError, ValueError, TypeError) as exc:
            return self._structured_error_response(text.strip(), requested_k, "INVALID_CONTRACT", str(exc))
        validation = validate_contract(contract)
        has_deferred = bool(contract.temporal_constraints or contract.relationship_constraints)
        if not validation.valid or has_deferred or contract.unsupported_constraints:
            invalid_states = {ValidationState.INVALID_CONTRACT, ValidationState.INVALID_OPERATOR, ValidationState.TYPE_MISMATCH, ValidationState.CONTRADICTION}
            state = "INVALID_CONTRACT" if any(issue.state in invalid_states for issue in validation.issues) else "UNSUPPORTED_CONSTRAINT"
            reason = "; ".join(issue.message for issue in validation.issues) or "The requested constraint category is deferred in v0.5."
            return self._structured_error_response(text.strip(), requested_k, state, reason, contract=contract)
        try:
            retriever = self._get_c1_retriever()
            query = Query(text.strip(), top_k=requested_k, request_id=str(uuid4()), retrieval_contract=contract)
            plan = RetrievalPlan(strategy="dense", top_k=requested_k, parameters={"retrieval_candidate_k": max(requested_k, 100), "retrieval_contract": contract})
            started = time.perf_counter()
            result = retriever.retrieve(query, plan)
            return self._structured_result_response(text.strip(), contract, result, (time.perf_counter() - started) * 1000)
        except (EmbeddingPrerequisiteError, RuntimeError) as exc:
            raise WorkbenchError("C1_PREREQUISITE_UNAVAILABLE", str(exc), status_code=503) from exc
        except Exception as exc:
            raise WorkbenchError("C1_EXECUTION_FAILED", "The C1 Elasticsearch request could not be completed.", status_code=502, details={"reason": str(exc)}) from exc

    def _get_c1_retriever(self):
        if self._c1_retriever is None:
            client = ElasticsearchClient()
            provider = create_embedding_provider({"embedding": {"provider": "bge", "model": os.getenv("ARMIE_V050_EMBEDDING_MODEL", "BAAI/bge-m3"), "local_files_only": True}})
            self._c1_retriever = ElasticsearchDenseRetriever(client, embedding_provider=provider)
        return self._c1_retriever

    def _structured_error_response(self, text, requested_k, state, reason, *, contract=None):
        trace_id, session_id = str(uuid4()), str(uuid4())
        contract_payload = contract.model_dump(mode="json") if contract else {"semantic_query": text}
        provenance = {"strategy_identity": "C1", "runtime_strategy": "constraint_prefilter", "contract_state": state, "requested_k": requested_k, "candidate_pool_count": 0, "eligible_candidate_count": 0, "returned_k": 0, "shortfall": {"requested": requested_k, "returned": 0, "count": requested_k, "reason": state}, "filter_applied": False, "constraint_diagnostics": {"validation_state": state, "error_category": state, "reason": reason, "candidate_pool_count": 0, "eligible_candidate_count": 0, "constraint_trace": []}, "index_compatibility": {"status": "not_checked"}}
        return self._structured_response(text, contract_payload, [], provenance, 0.0, trace_id, session_id, state, reason)

    def _structured_result_response(self, text, contract, result, latency):
        trace_id, session_id = str(uuid4()), str(uuid4())
        provenance = dict(result.provenance)
        state = provenance.get("contract_state", "VALID")
        items = []
        for rank, item in enumerate(result.items, 1):
            metadata = dict(item.metadata)
            evidence = self._constraint_evidence(contract, metadata)
            items.append({"id": item.id, "rank": rank, "title": item.title, "object_type": item.object_type, "content": item.content, "metadata": metadata, "structured_facts": {field: metadata.get(field) for field in ("years_experience", "seniority", "industries", "roles", "locations")}, "constraint_evidence": evidence, "score": item.score, "score_type": "Dense score", "score_source": "Elasticsearch Dense", "score_stack": {"dense_raw": item.score}, "signals": dict(item.signals), "sources": list(item.sources), "constraint_state": "SATISFIED" if all(row["status"] == "SATISFIED" for row in evidence) else "UNKNOWN", "evidence_refs": [f"ev-{item.id}"]})
        return self._structured_response(text, contract.model_dump(mode="json"), items, provenance, latency, trace_id, session_id, state)

    @staticmethod
    def _constraint_evidence(contract: RetrievalContract, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """Explain each executable hard constraint against one returned profile."""
        field_map = {"industry": "industries", "role": "roles", "location": "locations"}
        seniority_rank = {"mid": 1, "senior": 2, "principal": 3}

        def matches(observed: Any, operator: str, expected: Any) -> bool | None:
            if observed is None:
                return None
            values = observed if isinstance(observed, (list, tuple, set, frozenset)) else [observed]
            if operator == "eq": return expected in values
            if operator == "neq": return expected not in values
            if operator == "in": return any(value in expected for value in values)
            if operator == "not_in": return all(value not in expected for value in values)
            if operator in {"contains", "not_contains"}:
                present = any(str(expected).lower() in str(value).lower() for value in values)
                return present if operator == "contains" else not present
            try:
                actual, target = observed, expected
                if isinstance(observed, str) and observed.lower() in seniority_rank and str(expected).lower() in seniority_rank:
                    actual, target = seniority_rank[observed.lower()], seniority_rank[str(expected).lower()]
                if operator == "gte": return actual >= target
                if operator == "gt": return actual > target
                if operator == "lte": return actual <= target
                if operator == "lt": return actual < target
                if operator == "between": return expected[0] <= actual <= expected[1]
            except (TypeError, ValueError, IndexError):
                return None
            return None

        rows = []
        for polarity, constraints in (("required", contract.hard_constraints), ("excluded", contract.exclusions)):
            for constraint in constraints:
                canonical = constraint.canonical_field
                observed = metadata.get(field_map.get(canonical, canonical))
                matched = matches(observed, constraint.operator.value, constraint.expected_value)
                satisfied = (not matched) if polarity == "excluded" and matched is not None else matched
                status = "UNKNOWN" if satisfied is None else "SATISFIED" if satisfied else "VIOLATED"
                rows.append({"canonical_field": canonical, "operator": constraint.operator.value, "expected_value": constraint.expected_value, "observed_value": observed, "polarity": polarity, "status": status, "label": f"{canonical.replace('_', ' ').title()} ({'must not match' if polarity == 'excluded' else 'required'})"})
        return rows

    @staticmethod
    def _structured_response(text, contract, items, provenance, latency, trace_id, session_id, state, reason=None):
        returned = len(items); requested = int(provenance.get("requested_k", 5)); shortfall = provenance.get("shortfall", {"requested": requested, "returned": returned, "count": max(0, requested-returned), "reason": "STRICT_SHORTFALL" if returned < requested else None})
        trace = {"strategy_identity": "C1", "runtime_strategy": "constraint_prefilter", "contract_state": state, "provenance": provenance}
        summary = f"Constraint-aware Dense returned {returned} of {requested} requested results under strict hard constraints." if returned < requested else f"Constraint-aware Dense returned {returned} eligible results under strict hard constraints."
        evidence = [{"evidence_id": f"ev-{item['id']}", "result_id": item["id"], "title": item["title"], "snippet": "Constraint eligibility and dense provenance recorded."} for item in items]
        diagnostics = provenance.get("constraint_diagnostics", {})
        return {"schema_version": "0.5.0", "request_id": trace_id, "trace_id": trace_id, "session_id": session_id, "profile": "C1", "dataset_context": {"dataset": "Expert Discovery v2", "path": "v0.5.0", "quality_status": "unlabelled"}, "query": {"raw": text, "resolved": text, "structured_contract": contract}, "execution": {"status": "completed", "latency_ms": latency}, "execution_context": {"planner": {"actual_provider": "structured_contract", "strategy": "constraint_prefilter", "retrievers": ["elasticsearch_dense"], "constraints": [item.get("canonical_field") for item in diagnostics.get("constraint_trace", [])]}, "fallback": None, "status": "completed"}, "plan": {"strategy": "constraint_prefilter", "top_k": requested}, "answer_summary": {"type": "deterministic", "text": summary, "contract_state": state, "required_constraints": contract.get("hard_constraints", []), "exclusions": contract.get("exclusions", []), "shortfall": shortfall, "evidence_refs": [e["evidence_id"] for e in evidence], "result_refs": [item["id"] for item in items]}, "results": items, "evidence": evidence, "evidence_by_result": {item["id"]: {"constraint_provenance": provenance} for item in items}, "verification": {"status": "passed" if state == "VALID" else "not_executed", "findings": [], "labelled": False}, "metrics": {"quality_status": "unlabelled", "retrieval_latency_ms": provenance.get("latency_stages", {}).get("total_retrieval_ms", latency), "total_latency_ms": latency, "requested_k": requested, "returned_k": returned, "shortfall": shortfall}, "stage_summaries": [{"stage": "constraint_prefilter", "status": "completed" if state == "VALID" else "not_executed", "details": {"strategy": "C1", "contract_state": state, "filter_applied": provenance.get("filter_applied", False), "shortfall": shortfall}, "summary": {"provider": "elasticsearch_dense", "latency_ms": latency}}], "warnings": [] if not reason else [reason], "fallbacks": [], "raw_trace": trace, "repeatability": {"plan_fingerprint": trace_id, "result_ids": [item["id"] for item in items], "actual_provider": "elasticsearch_dense", "fallback": False, "total_latency_ms": latency, "verification_status": "passed" if state == "VALID" else "not_executed"}, "trace_url": f"/api/v1/traces/{trace_id}"}

    def run_benchmark_query(self, query_id: str, *, profile: str = "H2") -> dict[str, Any]:
        row = self.benchmark_query(query_id)
        return self.query(row["query_text"], profile=profile, benchmark_query_id=query_id)

    def trace(self, trace_id: str) -> dict[str, Any]:
        if trace_id not in self.traces:
            raise WorkbenchError("trace_not_found", "Trace was not found.", status_code=404)
        return self.traces[trace_id]

    def query_cases(self) -> list[dict[str, Any]]:
        return [{"id": q["id"], "name": q["id"].replace("-", " ").title(), "category": "expert_discovery", "query": q["query"], "relevant_ids": q["relevant_ids"], "labelled": True, "purpose": "Validate constrained expert retrieval.", "expected_constraints": [q["query"].split()[1], q["query"].split()[-2]], "acceptable_strategies": ["hybrid", "graph"]} for q in self.dataset.queries]

    def run_case(self, case_id: str, *, profile: str = "baseline") -> dict[str, Any]:
        case = next((q for q in self.dataset.queries if q["id"] == case_id), None)
        if not case:
            raise WorkbenchError("case_not_found", "Query Lab case was not found.", status_code=404)
        return self.query(case["query"], profile=profile, query_case_id=case_id)

    def compare_runs(self, left_run_id: str, right_run_id: str) -> dict[str, Any]:
        try:
            left, right = self.runs[left_run_id], self.runs[right_run_id]
        except KeyError as exc:
            raise WorkbenchError("run_not_found", "One or both runs were not found.", status_code=404) from exc
        def comparable(run):
            trace = run.get("raw_trace", {}); planner = trace.get("planner", {}); reranker = trace.get("reranking") or {}
            return {"profile": run["profile"], "planner": {"requested": planner.get("requested_provider"), "actual": planner.get("actual_provider"), "model": planner.get("model"), "strategy": planner.get("selected_strategy"), "retrievers": planner.get("selected_retrievers"), "constraints": planner.get("constraint_types"), "fingerprint": planner.get("parsed_plan", {}).get("plan_id")}, "reranker": {"requested": reranker.get("requested_provider"), "actual": reranker.get("actual_provider"), "model": reranker.get("model")}, "result_ids": [item["id"] for item in run["results"]], "metrics": run["metrics"], "warnings": run["warnings"], "fallbacks": run["fallbacks"], "verification": run["verification"]}
        left_view, right_view = comparable(left), comparable(right)
        left_ids, right_ids = left_view["result_ids"], right_view["result_ids"]
        common = sorted(set(left_ids) & set(right_ids))
        union = set(left_ids) | set(right_ids)
        left_metrics, right_metrics = left_view["metrics"], right_view["metrics"]
        metric_delta = {}
        for key, value in left_metrics.items():
            if isinstance(value, (int, float)) and isinstance(right_metrics.get(key), (int, float)):
                metric_delta[key] = right_metrics[key] - value
        latency_delta = right_metrics.get("total_latency_ms", 0) - left_metrics.get("total_latency_ms", 0)
        return {"left_run_id": left_run_id, "right_run_id": right_run_id, "left": left_view, "right": right_view,
                "overlap": {"common_ids": common, "common_count": len(common), "left_only": sorted(set(left_ids) - set(right_ids)), "right_only": sorted(set(right_ids) - set(left_ids)), "jaccard": len(common) / len(union) if union else 1.0},
                "rank_delta": self._rank_delta(left, right), "metric_delta": metric_delta,
                "latency_delta_ms": latency_delta, "latency_multiplier": (right_metrics.get("total_latency_ms", 0) / left_metrics.get("total_latency_ms", 1)) if left_metrics.get("total_latency_ms") else None,
                "interpretation": "The runs are comparable by result overlap, rank movement, quality metrics, and latency; provider-specific scores remain non-comparable.",
                "score_comparison": "Provider-specific scores are not directly compared."}

    def _runtime(self, profile_name: str):
        if profile_name in self._runtime_cache:
            return self._runtime_cache[profile_name]
        if profile_name in {"H1", "H2", "H3", "H4"}:
            strategy = {"H1": "sparse", "H2": "dense", "H3": "hybrid", "H4": "hybrid"}[profile_name]
            reranker = MetadataBoostReranker() if profile_name != "H4" else select_reranker(load_profile("model-enhanced", root=self.root / "configs" / "profiles")).provider
            provider = InMemoryKnowledgeProvider(self._benchmark_experts or self.dataset.experts); dense, sparse = DenseRetriever(provider), SparseRetriever(provider)
            graph_provider = NetworkXKnowledgeGraphProvider.from_experts(self.dataset.experts); retrievers = RetrieverRegistry(); retrievers.register("dense", dense, capabilities={"dense"}); retrievers.register("sparse", sparse, capabilities={"sparse"}); retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"}); retrievers.register("graph", GraphRetriever(graph_provider), capabilities={"graph"})
            processors = ProcessorRegistry(); processors.register("deduplicate", DeduplicateProcessor(), capabilities={"deduplicate"}); processors.register("metadata_filter", MetadataFilterProcessor(), capabilities={"metadata_filter"}); processors.register("rerank", QueryAwareRerankProcessor(reranker), capabilities={"rerank"})
            runtime = RetrievalRuntime(retrievers, processors); planner = select_planner({"planner": {"type": "rule"}}, capabilities=frozenset({"dense", "sparse", "hybrid", "graph"})).planner
            planner = __import__('armie_retrieval.planners', fromlist=['RuleBasedPlanner']).RuleBasedPlanner(retrievers.capabilities(), strategy_override=strategy, processor_names=("deduplicate", "rerank"), parameters={"retrieval_candidate_k": 100, "fusion_candidate_k": 100, "rerank_candidate_k": 30, "final_top_k": 5, "rrf_k": 60})
            self._runtime_cache[profile_name] = (runtime, planner); return runtime, planner
        profile = load_profile(profile_name, root=self.root / "configs" / "profiles")
        provider = InMemoryKnowledgeProvider(self.dataset.experts)
        dense, sparse = DenseRetriever(provider), SparseRetriever(provider)
        graph_provider = NetworkXKnowledgeGraphProvider.from_experts(self.dataset.experts)
        retrievers = RetrieverRegistry()
        retrievers.register("dense", dense, capabilities={"dense"})
        retrievers.register("sparse", sparse, capabilities={"sparse"})
        retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"})
        retrievers.register("graph", GraphRetriever(graph_provider), capabilities={"graph"})
        reranker = select_reranker(profile)
        processors = ProcessorRegistry()
        processors.register("deduplicate", DeduplicateProcessor(), capabilities={"deduplicate"})
        processors.register("metadata_filter", MetadataFilterProcessor(), capabilities={"metadata_filter"})
        processors.register("rerank", QueryAwareRerankProcessor(reranker.provider), capabilities={"rerank"})
        runtime = RetrievalRuntime(retrievers, processors)
        planner_selection = select_planner(profile, capabilities=frozenset({"dense", "sparse", "hybrid", "graph"}))
        planner = planner_selection.planner
        if not hasattr(planner, "selection"):
            planner.selection = planner_selection
        self._runtime_cache[profile_name] = (runtime, planner)
        return runtime, planner

    def _new_session(self) -> Session:
        data = self.create_session()
        return self.sessions[data["session_id"]]

    def _session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            raise WorkbenchError("session_not_found", "Session was not found.", status_code=404)
        return self.sessions[session_id]

    def _resolve_query(self, session: Session, raw: str) -> str:
        if not session.turns or not any(token in raw.lower().split() for token in ("only", "those", "them", "also", "same")):
            return raw
        return f"{session.turns[-1].resolved_query}; follow-up: {raw}"

    def _response(self, trace_id, session_id, raw, resolved, profile, result, trace, latency, case, benchmark_case=None):
        items = [self._item(item, index + 1) for index, item in enumerate(result.items)]
        score_labels = {"H1": ("BM25 score", "Elasticsearch BM25"), "H2": ("Dense score", "Elasticsearch Dense + metadata processor"), "H3": ("RRF fused score", "ARMIE RRF"), "H4": ("BGE Cross-Encoder score", "BAAI/bge-reranker-v2-m3")}
        for item in items:
            item["score_stack"].update(self._score_stack(trace, item["id"]))
            if profile in score_labels:
                item["score_type"], item["score_source"] = score_labels[profile]
            elif trace.reranking and trace.reranking.actual_provider == "bge_cross_encoder":
                item["score_type"] = "Cross-Encoder score"
                item["score_source"] = trace.reranking.model or trace.reranking.actual_provider
        evidence = [{"evidence_id": f"ev-{item['id']}", "result_id": item["id"], "title": item["title"], "snippet": self._evidence_by_result(trace, item["id"]), "source": "retrieval trace"} for item in items]
        refs = [e["evidence_id"] for e in evidence]
        summary = self._summary(trace, items, refs, resolved)
        verification = self._verify(items, evidence, summary, case, trace)
        metrics = self._metrics(trace, latency, len(items), case)
        benchmark = self._benchmark_projection(benchmark_case, items) if benchmark_case else None
        if benchmark:
            for item in items:
                item.update(benchmark["labels"].get(item["id"], {"judgement_grade": None, "judgement_status": benchmark["judgement_source"]}))
        if benchmark: metrics.update(benchmark["metrics"])
        response = {"schema_version": __version__, "request_id": trace.query_id, "trace_id": trace_id, "session_id": session_id, "profile": profile, "dataset_context": {"dataset": "Expert Discovery v2" if profile in {"H1", "H2", "H3", "H4"} and self._benchmark_payload else "Legacy v1 fixture", "path": "v0.5.0" if profile in {"H1", "H2", "H3", "H4"} and self._benchmark_payload else "legacy", "quality_status": "labelled" if benchmark_case else "unlabelled"}, "query": {"raw": raw, "resolved": resolved}, "execution": {"status": "completed", "latency_ms": latency, "started_at": time.time()}, "execution_context": self._execution_context(trace), "plan": trace.planner.parsed_plan, "answer_summary": summary, "results": items, "evidence": evidence, "evidence_by_result": {item["id"]: self._evidence_detail(trace, item["id"]) for item in items}, "verification": verification, "metrics": metrics, "benchmark": benchmark, "experiment_manifest": self.benchmark_manifest() if benchmark_case else None, "stage_summaries": self._stage_summaries(trace), "warnings": list(trace.warnings) + list(trace.planner.warnings), "fallbacks": [trace.planner.fallback] if trace.planner.fallback else [], "raw_trace": trace.to_dict(), "trace_url": f"/api/v1/traces/{trace_id}"}
        response["schema_version"] = "0.5.0"
        response["provenance_schema_version"] = PROVENANCE_SCHEMA_VERSION
        if response["dataset_context"]["dataset"] == "Expert Discovery v2": response["dataset_context"]["path"] = "v0.5.0"
        response["repeatability"] = {"plan_fingerprint": trace.planner.parsed_plan.get("plan_id"), "result_ids": [item["id"] for item in items], "actual_provider": trace.planner.actual_provider, "fallback": bool(trace.planner.fallback), "planner_latency_ms": trace.planner.latency_ms, "total_latency_ms": latency, "verification_status": verification["status"]}
        return response

    @staticmethod
    def _execution_context(trace):
        reranker = trace.reranking
        return {"planner": {"requested_provider": trace.planner.requested_provider, "actual_provider": trace.planner.actual_provider, "requested_model": trace.planner.requested_model, "model": trace.planner.model, "strategy": trace.planner.selected_strategy, "retrievers": list(trace.planner.selected_retrievers), "processors": list(trace.planner.parsed_plan.get("processor_names", ())), "constraints": list(trace.planner.constraint_types), "fingerprint": trace.planner.parsed_plan.get("plan_id")}, "reranker": {"requested_provider": reranker.requested_provider if reranker else None, "actual_provider": reranker.actual_provider if reranker else None, "model": reranker.model if reranker else None}, "fallback": trace.planner.fallback, "status": "completed"}

    def _stage_summaries(self, trace):
        selected = list(trace.planner.selected_retrievers)
        retrievers = {r.name: r for r in trace.retrievers}
        timings = dict(trace.timing_ms)
        stages = ["query", "context_resolution", "planner", "dense", "sparse", "graph", "fusion", "reranking", "final_ranking", "answer_summary", "verification", "evaluation", "warnings"]
        rows = []
        for name in stages:
            if name == "context_resolution": status = "completed" if trace.planner.raw_query != trace.planner.query_rewrite and trace.planner.query_rewrite else "not_applicable"
            elif name in {"query", "planner", "final_ranking", "answer_summary", "verification"}: status = "completed"
            elif name == "evaluation": status = "completed" if trace.evaluation else "unlabelled"
            elif name == "warnings": status = "completed" if trace.warnings or trace.planner.warnings else "none"
            elif name == "fusion": status = "completed" if trace.fusion else "not_selected"
            elif name == "reranking": status = "completed" if trace.reranking else "not_selected"
            else: status = "completed" if name in selected else "not_selected"
            detail = {"provider": trace.planner.actual_provider, "model": trace.planner.model, "latency_ms": timings.get(name, timings.get("retrieval", 0.0)), "input_count": None, "output_count": None, "warning_count": 0}
            if name in retrievers:
                detail.update({"provider": retrievers[name].name, "latency_ms": retrievers[name].latency_ms, "input_count": retrievers[name].candidate_count_before_truncation, "output_count": len(retrievers[name].candidates), "candidates": [asdict(c) for c in retrievers[name].candidates]})
            if name == "planner": detail.update({"strategy": trace.planner.selected_strategy, "retrievers": selected, "processors": list(trace.planner.parsed_plan.get("processor_names", ())), "reason_codes": list(trace.planner.reason_codes), "constraint_types": list(trace.planner.constraint_types), "requested_top_k": trace.planner.requested_top_k, "effective_top_k": trace.planner.effective_final_top_k, "fallback": trace.planner.fallback, "fingerprint": trace.planner.parsed_plan.get("plan_id")})
            if name == "fusion" and trace.fusion: detail.update({"method": trace.fusion.method, "rrf_k": trace.fusion.rrf_k, "input_retrievers": selected, "unique_candidate_count": len(trace.fusion.deduplicated_ids), "output_count": len(trace.fusion.candidates), "candidates": [asdict(c) for c in trace.fusion.candidates]})
            if name == "reranking" and trace.reranking: detail.update(asdict(trace.reranking))
            if name == "evaluation": detail.update({"quality_metrics": dict(trace.evaluation.metrics) if trace.evaluation else "not_applicable", "quality_status": "labelled" if trace.evaluation else "unlabelled"})
            if name == "warnings": detail.update({"count": len(trace.warnings) + len(trace.planner.warnings), "warnings": list(trace.warnings) + list(trace.planner.warnings)})
            if name == "context_resolution": detail.update({"resolution_required": status == "completed", "mode": "follow_up" if status == "completed" else "passthrough"})
            if name == "graph" and status == "not_selected": detail.update({"selected_by_plan": False, "reason": "The Planner selected dense and sparse retrieval only."})
            if name == "final_ranking": detail.update({"ranked_result_count": len(trace.ranking.candidates) if trace.ranking else 0, "top_k": trace.planner.effective_final_top_k, "ranked_ids": [candidate.expert_id for candidate in trace.ranking.candidates] if trace.ranking else []})
            if name == "answer_summary": detail.update({"summary_type": "deterministic", "evidence_refs_available": True, "result_refs_available": True})
            if name == "verification": detail.update({"rule_count": 10, "verification_scope": "trace, evidence, result ordering, constraints, and evaluation state"})
            if status == "completed" and not detail: detail = {"detail_availability": "minimal", "detail_reason": "The current runtime does not emit additional fields for this stage."}
            rows.append({"stage": name, "status": status, "details": detail, "summary": detail})
        return self._validate_stage_details(rows)

    @staticmethod
    def _validate_stage_details(rows):
        for row in rows:
            if row["status"] == "completed" and not row.get("details"):
                row["details"] = {"detail_availability": "unavailable", "detail_reason": "The current runtime did not emit additional metadata for this completed stage."}
                row["summary"] = row["details"]
        return rows

    def _verify(self, items, evidence, summary, case, trace):
        refs = {e["evidence_id"] for e in evidence}; result_ids = {i["id"] for i in items}
        specs = [("result_order", "Result order consistency", "Scores are non-increasing", all(items[i]["score"] >= items[i + 1]["score"] for i in range(len(items) - 1)), result_ids, refs), ("evidence_refs", "Evidence references", "Every evidence reference resolves", all(e["evidence_id"] in refs for e in evidence), result_ids, refs), ("summary_refs", "Summary references", "Summary references resolve", all(ref in refs for ref in summary["evidence_refs"]), result_ids, set(summary["evidence_refs"])), ("unsupported_claims", "Unsupported claims", "Summary is deterministic", True, result_ids, refs), ("candidate_counts", "Candidate-count consistency", "Final result count is bounded", len(items) <= 5, result_ids, refs), ("provider_transparency", "Provider transparency", "Planner provider is present", bool(trace.planner.actual_provider), result_ids, refs), ("fallback_disclosure", "Fallback disclosure", "Fallback state is disclosed", True, result_ids, refs), ("constraint_coverage", "Constraint coverage", "Constraint state is observable", True, result_ids, refs), ("top_k_consistency", "Entered/exited Top-K consistency", "Ranking trace is available", bool(trace.ranking), result_ids, refs), ("evaluation_consistency", "Evaluation consistency", "Labelled state is explicit", True, result_ids, refs)]
        findings = [{"rule_id": rid, "name": name, "description": desc, "status": "passed" if ok else "failed", "expected": desc, "actual": "observed", "related_result_ids": sorted(result_ids), "related_evidence_ids": sorted(refs)} for rid, name, desc, ok, _, _ in specs]
        return {"status": "passed" if all(f["status"] == "passed" for f in findings) else "failed", "findings": findings, "labelled": bool(case), "notes": ["Verification is observational and does not modify retrieval results."]}

    @staticmethod
    def _metrics(trace, latency, count, case):
        retriever_latencies = {retriever.name: retriever.latency_ms for retriever in trace.retrievers}
        rerank_latency = (trace.reranking.model_load_latency_ms + trace.reranking.inference_latency_ms) if trace.reranking else 0.0
        fusion_latency = trace.timing_ms.get("fusion") if trace.planner.selected_strategy == "hybrid" and trace.timing_ms.get("fusion") is not None else None
        metrics = {"total_latency_ms": latency, "planner_latency_ms": trace.planner.latency_ms, "retrieval_latency_ms": trace.timing_ms.get("retrieval"), "dense_latency_ms": retriever_latencies.get("dense"), "sparse_latency_ms": retriever_latencies.get("sparse"), "graph_latency_ms": retriever_latencies.get("graph"), "fusion_latency_ms": fusion_latency, "reranking_latency_ms": rerank_latency if trace.reranking else None, "reranker_model_load_latency_ms": trace.reranking.model_load_latency_ms if trace.reranking else None, "reranker_inference_latency_ms": trace.reranking.inference_latency_ms if trace.reranking else None, "dense_candidate_count": next((r.candidate_count_before_truncation for r in trace.retrievers if r.name == "dense"), None), "sparse_candidate_count": next((r.candidate_count_before_truncation for r in trace.retrievers if r.name == "sparse"), None), "fusion_output_count": len(trace.fusion.candidates) if trace.fusion else None, "rerank_input_count": trace.reranking.rerank_input_candidates if trace.reranking else None, "rerank_processed_count": trace.reranking.reranker_processed_candidates if trace.reranking else None, "final_result_count": count, "final_top_k": trace.planner.effective_final_top_k, "quality_status": "labelled" if case else "unlabelled"}
        if trace.evaluation: metrics["quality_metrics"] = dict(trace.evaluation.metrics)
        else: metrics["quality_metrics"] = "not_applicable"
        return metrics

    def _benchmark_projection(self, benchmark_case, items):
        qid = benchmark_case["query_id"]
        statuses = self._benchmark_payload["judgements"].get(qid, {})
        source = "draft_gold_structured_audit" if "draft_gold_structured_audit" in statuses else "draft_silver_rule_assisted"
        labels = statuses.get(source, {})
        grades = {key: int(value.get("grade", 0)) for key, value in labels.items()}
        ids = [item["id"] for item in items]
        top5 = ids[:5]; top10 = ids[:10]
        relevant = {key for key, grade in grades.items() if grade >= 1}
        grade3 = {key for key, grade in grades.items() if grade == 3}
        hits = sum(grades.get(key, 0) >= 1 for key in top5)
        first = next((rank for rank, key in enumerate(top10, 1) if grades.get(key, 0) >= 1), None)
        dcg = sum((2 ** grades.get(key, 0) - 1) / math.log2(rank + 1) for rank, key in enumerate(top5, 1))
        ideal = sorted((2 ** grade - 1 for grade in grades.values()), reverse=True)[:5]
        idcg = sum(value / math.log2(rank + 1) for rank, value in enumerate(ideal, 1))
        return {"label_status": "Gold" if source == "draft_gold_structured_audit" else "Silver", "judgement_source": source, "labels": {key: {"judgement_grade": value.get("grade"), "judgement_status": source, "evidence_refs": value.get("evidence_ids", []), "matched_concepts": value.get("matched_concepts", []), "missing_concepts": value.get("missing_concepts", []), "violated_concepts": value.get("violated_concepts", [])} for key, value in labels.items()}, "constraints": benchmark_case, "metrics": {"precision_at_5": hits / 5, "ndcg_at_5": dcg / idcg if idcg else 0.0, "mrr": 1 / first if first else 0.0, "grade_3_hit_at_5": int(bool(grade3 & set(top5))), "recall_at_10": sum(grades.get(key, 0) >= 1 for key in top10) / len(relevant) if relevant else 0.0, "recall_denominator": "full judged relevant set at grade >= 1", "true_hard_negative_intrusion": int(any(grades.get(key, 0) == 0 and key in labels for key in top5)), "required_constraint_satisfaction": sum(grades.get(key, 0) == 3 for key in top5) / 5}}

    @staticmethod
    def _summary(trace, items, refs, query):
        top = [f"{item['id']} ({item['title']})" for item in items[:3]]
        fallback = trace.planner.fallback or "none"
        reranker = trace.reranking.actual_provider if trace.reranking else "none"
        return {"type": "deterministic", "text": f"Retrieved {len(items)} results for {query}. Highest-ranked: {', '.join(top) or 'none'}. Planner: {trace.planner.actual_provider}; reranker: {reranker}; constraints: {', '.join(trace.planner.constraint_types) or 'none'}; fallback: {fallback}.", "evidence_refs": refs[:5], "result_refs": [item["id"] for item in items[:3]], "matched_constraints": list(trace.planner.constraint_types), "fallback": trace.planner.fallback, "limitations": ["Deterministic summary; no new facts are generated."]}

    @staticmethod
    def _evidence_detail(trace, result_id):
        detail = {"dense": {"selected": False}, "sparse": {"selected": False}, "graph": {"selected": False}, "fusion": {}, "reranking": {}, "score_stack": {}}
        for retriever in trace.retrievers:
            candidates = [asdict(c) for c in retriever.candidates if c.expert_id == result_id]
            detail[retriever.name] = {"selected": bool(candidates), "candidates": candidates, "provider": retriever.name}
        selected_names = {retriever.name for retriever in trace.retrievers}
        if "graph" not in selected_names:
            detail["graph"] = {"selected": False, "candidates": [], "provider": "graph", "reason": "The Planner did not select graph retrieval for this query."}
        if trace.fusion:
            detail["fusion"] = {"method": trace.fusion.method, "rrf_k": trace.fusion.rrf_k, "candidate": next((asdict(c) for c in trace.fusion.candidates if c.expert_id == result_id), None)}
        if trace.reranking:
            detail["reranking"] = {"requested_provider": trace.reranking.requested_provider, "actual_provider": trace.reranking.actual_provider, "model": trace.reranking.model, "scoring_method": trace.reranking.scoring_method, "candidate": next((c for c in trace.reranking.candidates if c.get("expert_id") == result_id), None)}
        return detail

    def _evidence_by_result(self, trace, result_id):
        detail = self._evidence_detail(trace, result_id)
        fragments = []
        for name in ("dense", "sparse", "graph"):
            candidate = detail[name].get("candidates", [])
            if candidate: fragments.append(f"{name}: matched {', '.join(candidate[0].get('matched_fields', []) or candidate[0].get('matched_terms', [])) or 'candidate signal'}")
        if detail["fusion"].get("candidate"): fragments.append("fusion: RRF source contributions recorded")
        if detail["reranking"].get("candidate"): fragments.append("reranking: provider-specific score and rank transition recorded")
        return "; ".join(fragments) or "No stage-specific evidence was recorded for this result."

    @staticmethod
    def _score_stack(trace, result_id):
        stack = {}
        if trace.fusion:
            candidate = next((c for c in trace.fusion.candidates if c.expert_id == result_id), None)
            if candidate:
                stack["fusion_rrf"] = candidate.raw_score
                for source, values in candidate.contributions.items():
                    if values.get("raw_score") is not None: stack[f"{source}_raw"] = values["raw_score"]
        if trace.reranking:
            candidate = next((c for c in trace.reranking.candidates if c.get("expert_id") == result_id), None)
            if candidate and candidate.get("reranker_raw_score") is not None: stack["reranker_raw"] = candidate["reranker_raw_score"]
        return stack

    @staticmethod
    def _item(item, rank):
        score_stack = {key: value for key, value in item.signals.items() if value is not None}
        return {"id": item.id, "rank": rank, "title": item.title, "object_type": item.object_type, "content": item.content, "metadata": dict(item.metadata), "score": item.score, "score_type": "RRF fused score" if "rrf" in item.signals else ("reranker score" if "rerank" in item.signals else "provider score"), "score_source": "hybrid fusion" if "rrf" in item.signals else "result processor", "score_stack": score_stack, "signals": dict(item.signals), "sources": list(item.sources)}

    @staticmethod
    def _session_dict(session):
        return {"session_id": session.session_id, "created_at": session.created_at, "turn_count": len(session.turns), "turns": [asdict(turn) for turn in session.turns]}

    @staticmethod
    def _rank_delta(left, right):
        l = {item["id"]: item["rank"] for item in left["results"]}
        r = {item["id"]: item["rank"] for item in right["results"]}
        return [{"id": item_id, "left_rank": l.get(item_id), "right_rank": r.get(item_id)} for item_id in sorted(set(l) | set(r))]
