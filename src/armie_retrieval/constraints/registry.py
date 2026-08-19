"""Authoritative runtime capability registry for Gate 7 C1 retrieval.

This is deliberately a small, explicit registry.  It is not a query parser and
it does not infer constraints from natural language; it describes the contract
surface that the native Elasticsearch pre-filter is allowed to execute.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from armie_retrieval.contracts import ConstraintOperator


@dataclass(frozen=True)
class ConstraintCapability:
    canonical_field: str
    projection_field: str
    operators: tuple[ConstraintOperator, ...]
    status: str = "supported"
    scope: str = "profile"


SUPPORTED_CONSTRAINTS: tuple[ConstraintCapability, ...] = (
    ConstraintCapability("industry", "industries", (ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN)),
    ConstraintCapability("role", "roles", (ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN)),
    ConstraintCapability("location", "locations", (ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN)),
    ConstraintCapability("years_experience", "years_experience", (ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT, ConstraintOperator.BETWEEN)),
    ConstraintCapability("seniority", "seniority_rank", (ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT)),
)

DEFERRED_CONSTRAINTS = {
    "temporal": "deferred_temporal_scope",
    "relationship": "deferred_relationship_scope",
    "evidence": "deferred_evidence_scope",
    "delivery": "deferred_delivery_scope",
}

# Canonical categorical values are exposed by the backend registry so clients
# never need to maintain a second vocabulary. These are projection values, not
# natural-language extraction hints.
CANONICAL_VALUES = {
    "industry": ("healthcare", "financial services", "energy", "retail", "manufacturing", "technology"),
}

REGISTRY_ID = "v0.5-c1-capability-registry-1"
REGISTRY_SCHEMA_VERSION = "constraint-registry-v1"
DISPLAY_LABELS = {value: value.title() for value in CANONICAL_VALUES["industry"]}


def capability_registry() -> dict[str, dict]:
    return {
        item.canonical_field: {
            "canonical_field": item.canonical_field,
            "projection_field": item.projection_field,
            "operators": [op.value for op in item.operators],
            "status": item.status,
            "scope": item.scope,
            **({"values": list(CANONICAL_VALUES[item.canonical_field]), "display_labels": dict(DISPLAY_LABELS)} if item.canonical_field in CANONICAL_VALUES else {}),
        }
        for item in SUPPORTED_CONSTRAINTS
    }


def get_capability(field: str) -> ConstraintCapability | None:
    return next((item for item in SUPPORTED_CONSTRAINTS if item.canonical_field == field), None)


def supported_fields() -> tuple[str, ...]:
    return tuple(item.canonical_field for item in SUPPORTED_CONSTRAINTS)


def supported_operators(field: str) -> tuple[str, ...]:
    item = get_capability(field)
    return tuple(op.value for op in item.operators) if item else ()


def registry_snapshot() -> dict:
    return {"registry_id": REGISTRY_ID, "version": REGISTRY_ID, "schema_version": REGISTRY_SCHEMA_VERSION, "compatibility": {"patch": "display aliases only; canonical semantics unchanged", "minor": "new supported field/operator with explicit registry version", "breaking": "canonical value or operator meaning changes"}, "supported": capability_registry(), "deferred": dict(DEFERRED_CONSTRAINTS)}
