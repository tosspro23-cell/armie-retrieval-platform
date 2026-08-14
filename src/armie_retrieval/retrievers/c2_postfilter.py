"""Controlled C2 post-filter over an existing Dense candidate pool."""
from __future__ import annotations

import time
from dataclasses import replace
from typing import Any

from armie_retrieval.constraints import ConstraintPlan, ConstraintPolarity, ElasticsearchConstraintCompiler
from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult


def _observed(item: Any, field: str) -> Any:
    metadata = item.metadata
    if field == "seniority_rank":
        return metadata.get("seniority_rank")
    return metadata.get(field)


def verify_candidate(item: Any, plans: tuple[ConstraintPlan, ...]) -> tuple[bool, tuple[dict[str, Any], ...]]:
    decisions: list[dict[str, Any]] = []
    eligible = True
    for plan in plans:
        if not plan.executable:
            decisions.append({"constraint_id": plan.constraint_id, "status": "UNKNOWN", "reason_code": plan.reason or "non_executable"})
            eligible = False
            continue
        observed = _observed(item, plan.projection_field or "")
        values = observed if isinstance(observed, (list, tuple, set, frozenset)) else (observed,)
        value = plan.value
        op = plan.operation.value if plan.operation else ""
        present = observed is not None
        if op == "eq": satisfied = present and (value in values)
        elif op == "neq": satisfied = present and (value not in values)
        elif op == "in": satisfied = present and bool(set(values) & set(value))
        elif op == "not_in": satisfied = present and not (set(values) & set(value))
        elif op in {"gte", "gt", "lte", "lt"}:
            satisfied = present and {"gte": observed >= value, "gt": observed > value, "lte": observed <= value, "lt": observed < value}[op]
        elif op == "between": satisfied = present and value[0] <= observed <= value[1]
        else: satisfied = False
        excluded_violation = plan.polarity is ConstraintPolarity.EXCLUDED and satisfied
        effective_satisfied = (not satisfied) if plan.polarity is ConstraintPolarity.EXCLUDED else satisfied
        status = "SATISFIED" if effective_satisfied else ("VIOLATED" if present else "UNKNOWN")
        decisions.append({"constraint_id": plan.constraint_id, "canonical_field": plan.canonical_field, "projection_field": plan.projection_field, "operator": op, "expected_value": value, "observed_value": observed, "status": status})
        if plan.polarity is ConstraintPolarity.REQUIRED and not satisfied:
            eligible = False
        if excluded_violation:
            eligible = False
    return eligible, tuple(decisions)


class C2PostFilterRetriever:
    """Dense candidate pool plus deterministic verification; no reranking."""

    name = "c2_dense_postfilter"
    capabilities = frozenset({"dense", "c2_postfilter"})

    def __init__(self, dense_retriever: Any, *, candidate_pool_size: int = 30) -> None:
        if candidate_pool_size not in (10, 20, 30, 50, 100):
            raise ValueError("candidate_pool_size must be one of 10, 20, 30, 50, 100")
        self.dense_retriever = dense_retriever
        self.candidate_pool_size = candidate_pool_size

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        contract = query.retrieval_contract or plan.parameters.get("retrieval_contract")
        if contract is None:
            return self.dense_retriever.retrieve(query, plan)
        semantic_plans = ElasticsearchConstraintCompiler().plan(contract)
        deferred = bool(getattr(contract, "temporal_constraints", ())) or bool(getattr(contract, "relationship_constraints", ()))
        if deferred or any(not item.executable for item in semantic_plans):
            return RetrievalResult(items=(), plan_id=plan.plan_id, strategy="c2", latency_ms=(time.perf_counter() - started) * 1000, provenance={"strategy_identity": "C2", "constraint_diagnostics": {"validation_state": "NON_EXECUTABLE", "candidate_pool_size": self.candidate_pool_size, "non_executable_constraint_count": sum(not p.executable for p in semantic_plans), "returned_result_count": 0}}, trace=("constraint:c2_non_executable",))
        pool_plan = replace(plan, top_k=self.candidate_pool_size, parameters={**plan.parameters, "retrieval_candidate_k": self.candidate_pool_size})
        # Candidate retrieval is intentionally unconstrained C0/H2; the
        # semantic contract is verified only after the explicit pool is formed.
        dense_query = Query(query.text, domain=query.domain, filters=query.filters, top_k=query.top_k, request_id=query.request_id, retrieval_contract=None)
        dense = self.dense_retriever.retrieve(dense_query, pool_plan)
        verification_started = time.perf_counter()
        eligible_items = []
        audit = []
        counts = {"SATISFIED": 0, "VIOLATED": 0, "UNKNOWN": 0}
        for item in dense.items:
            eligible, decisions = verify_candidate(item, semantic_plans)
            candidate_status = "SATISFIED"
            if any(decision["status"] == "UNKNOWN" for decision in decisions):
                candidate_status = "UNKNOWN"
            elif any(decision["status"] == "VIOLATED" for decision in decisions):
                candidate_status = "VIOLATED"
            counts[candidate_status] += 1
            audit.append({"candidate_id": item.id, "eligible": eligible, "constraints": decisions})
            if eligible: eligible_items.append(item)
        verification_ms = (time.perf_counter() - verification_started) * 1000
        selected = tuple(eligible_items[:plan.top_k])
        provenance = dict(dense.provenance)
        provenance.update({"strategy_identity": "C2", "candidate_pool_size": self.candidate_pool_size, "candidate_count_retrieved": len(dense.items), "eligible_count": len(eligible_items), "strict_shortfall_count": max(0, plan.top_k - len(selected)), "verification_counts": counts, "verification_latency_ms": verification_ms, "total_retrieval_ms": (time.perf_counter() - started) * 1000, "verification_audit": audit})
        return RetrievalResult(items=selected, plan_id=plan.plan_id, strategy="c2", latency_ms=(time.perf_counter() - started) * 1000, provenance=provenance, trace=(*dense.trace, "constraint:c2_postfilter"))
