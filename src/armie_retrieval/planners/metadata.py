"""Finite, observable planner-decision metadata; never chain-of-thought."""

from __future__ import annotations

import re
from typing import Any, Mapping

from armie_retrieval.models import Query


REASON_CODES = frozenset({
    "semantic_similarity_required", "exact_term_matching_helpful", "entity_relationship_query",
    "multiple_structured_constraints", "single_semantic_intent", "graph_constraints_available",
    "hybrid_signal_coverage", "latency_sensitive", "fallback_safe_strategy",
})
CONSTRAINT_TYPES = frozenset({"skill", "industry", "organization", "relationship", "technology", "country"})

_KNOWN_SKILLS = ("azure ai", "rag", "knowledge graph", "faiss", "semantic search", "mlops", "microsoft cloud")
_KNOWN_INDUSTRIES = ("healthcare", "financial services", "energy", "retail", "manufacturing")


def planner_metadata(response: Mapping[str, Any] | None, query: Query) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Normalize optional structured planner fields and report invalid labels."""
    payload = response or {}
    text = re.sub(r"\s+", " ", query.text.lower())
    skills = _string_tuple(payload.get("skills"), _phrases(text, _KNOWN_SKILLS))
    industries = _string_tuple(payload.get("industries"), _phrases(text, _KNOWN_INDUSTRIES))
    organizations = _string_tuple(payload.get("organizations"), ())
    requested_codes = _string_tuple(payload.get("reason_codes"), ())
    requested_types = _string_tuple(payload.get("constraint_types"), ())
    inferred_types = tuple(
        kind for kind, values in (("skill", skills), ("industry", industries), ("organization", organizations)) if values
    )
    codes = tuple(code for code in requested_codes if code in REASON_CODES)
    types = tuple(kind for kind in requested_types if kind in CONSTRAINT_TYPES) or inferred_types
    warnings = tuple(
        [f"Ignored unsupported planner reason code: {code}" for code in requested_codes if code not in REASON_CODES]
        + [f"Ignored unsupported planner constraint type: {kind}" for kind in requested_types if kind not in CONSTRAINT_TYPES]
    )
    return {
        "skills": skills,
        "industries": industries,
        "organizations": organizations,
        "reason_codes": codes,
        "constraint_types": types,
        "requested_retrievers": _string_tuple(payload.get("retrievers"), ()),
    }, warnings


def routing_warnings(*, strategy: str, selected_retrievers: tuple[str, ...], metadata: Mapping[str, Any]) -> tuple[str, ...]:
    """Observational diagnostics. These warnings never mutate a RetrievalPlan."""
    types = set(metadata.get("constraint_types", ()))
    requested = tuple(_canonical_retriever(value) for value in metadata.get("requested_retrievers", ()))
    selected_retrievers = tuple(_canonical_retriever(value) for value in selected_retrievers)
    canonical_strategy = _canonical_retriever(strategy)
    codes = set(metadata.get("reason_codes", ()))
    warnings: list[str] = []
    graph_representable = len(types & {"skill", "industry", "organization", "relationship"}) >= 2 or "relationship" in types
    if graph_representable and "graph" not in selected_retrievers:
        warnings.append("Planner extracted multiple graph-representable constraints but did not select graph.")
    if strategy == "dense" and types & {"skill", "organization", "technology"}:
        warnings.append("Planner selected dense-only despite exact lexical entities.")
    if strategy == "graph" and not graph_representable:
        warnings.append("Planner selected graph without graph-representable constraints.")
    if strategy == "hybrid" and len(selected_retrievers) <= 1:
        warnings.append("Planner selected hybrid but only one retriever was selected.")
    if requested and set(requested) != set(selected_retrievers):
        warnings.append("Planner requested retrievers do not match the strategy-backed runtime selection.")
    if codes and strategy == "hybrid" and "sparse" in selected_retrievers and not codes & {"exact_term_matching_helpful", "hybrid_signal_coverage"}:
        warnings.append("Hybrid plan selected sparse retrieval without an exact-term or hybrid coverage reason code.")
    if codes and canonical_strategy == "graph" and not codes & {"entity_relationship_query", "graph_constraints_available", "multiple_structured_constraints"}:
        warnings.append("Graph strategy selected without a graph-related reason code.")
    if codes and "dense" in selected_retrievers and not codes & {"semantic_similarity_required", "single_semantic_intent", "hybrid_signal_coverage"}:
        warnings.append("Dense strategy selected without a semantic-related reason code.")
    return tuple(warnings)


def _canonical_retriever(value: str) -> str:
    return "keyword" if value in {"sparse", "keyword"} else value


def _phrases(text: str, options: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(value for value in options if value in text)


def _string_tuple(value: Any, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value if isinstance(item, (str, int, float)))
    return default
