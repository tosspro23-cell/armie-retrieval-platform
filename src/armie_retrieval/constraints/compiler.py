"""Bounded semantic planning and deterministic Elasticsearch translation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from armie_retrieval.contracts import Constraint, ConstraintOperator, RetrievalContract, validate_contract
from .registry import get_capability

# Kept as a compatibility export for older callers.  The capability registry
# is the authoritative source for Gate 7 runtime support.
APPROVED = {"industry": "industries", "role": "roles", "location": "locations", "years_experience": "years_experience", "seniority": "seniority_rank"}
SENIORITY_RANK = {"mid": 1, "senior": 2, "principal": 3}


class ConstraintPolarity(str, Enum):
    REQUIRED = "REQUIRED"
    EXCLUDED = "EXCLUDED"


@dataclass(frozen=True)
class ConstraintPlan:
    """Backend-neutral semantic plan; ``dsl`` is populated only after translation."""

    constraint_id: str | None
    canonical_field: str | None
    projection_field: str | None
    scope: str
    operation: ConstraintOperator | None
    value: Any
    polarity: ConstraintPolarity
    executable: bool
    reason: str | None = None
    dsl: dict[str, Any] | None = None


class ElasticsearchConstraintCompiler:
    """Allow-list compiler. It never accepts user field names or raw DSL."""

    def plan(self, contract: RetrievalContract) -> tuple[ConstraintPlan, ...]:
        validation = validate_contract(contract)
        plans: list[ConstraintPlan] = []
        if not validation.valid:
            for issue in validation.issues:
                plans.append(ConstraintPlan(issue.constraint_id, None, None, "profile", None, None, ConstraintPolarity.REQUIRED, False, validation.state.value))
            return tuple(plans) or (ConstraintPlan(None, None, None, "profile", None, None, ConstraintPolarity.REQUIRED, False, validation.state.value),)
        for constraint in contract.hard_constraints:
            plans.append(self._semantic_plan(constraint, ConstraintPolarity.REQUIRED))
        for constraint in contract.exclusions:
            plans.append(self._semantic_plan(constraint, ConstraintPolarity.EXCLUDED))
        for unsupported in contract.unsupported_constraints:
            plans.append(ConstraintPlan(None, None, None, "profile", None, unsupported.expression, ConstraintPolarity.REQUIRED, False, "UNSUPPORTED_CONSTRAINT"))
        return tuple(plans)

    def compile(self, contract: RetrievalContract) -> tuple[ConstraintPlan, ...]:
        return tuple(self._translate(plan) for plan in self.plan(contract))

    def _semantic_plan(self, constraint: Constraint, polarity: ConstraintPolarity) -> ConstraintPlan:
        capability = get_capability(constraint.canonical_field)
        field = capability.projection_field if capability else None
        value = constraint.expected_value
        if capability and constraint.operator not in capability.operators:
            return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, field, "profile", constraint.operator, value, polarity, False, "unsupported_operator")
        if constraint.canonical_field == "seniority":
            if constraint.operator in (ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN):
                # Equality remains on the enum field; rank is only for ordered operations.
                field = "seniority"
            else:
                field = "seniority_rank"
            if isinstance(value, (list, tuple, set, frozenset)):
                values = list(value)
                if any(item not in SENIORITY_RANK for item in values):
                    return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, field, "profile", constraint.operator, value, polarity, False, "unknown_seniority")
                value = [SENIORITY_RANK[item] for item in values] if field == "seniority_rank" else sorted(values)
            elif field == "seniority" and value not in SENIORITY_RANK:
                return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, field, "profile", constraint.operator, value, polarity, False, "unknown_seniority")
            elif field == "seniority_rank":
                if value not in SENIORITY_RANK:
                    return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, field, "profile", constraint.operator, value, polarity, False, "unknown_seniority")
                value = SENIORITY_RANK[value]
        if not field:
            return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, None, "profile", constraint.operator, value, polarity, False, "unsupported_field")
        if constraint.operator in (ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS):
            return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, field, "profile", constraint.operator, value, polarity, False, "unsupported_operator")
        if isinstance(value, (set, frozenset, list, tuple)) and constraint.operator in (ConstraintOperator.IN, ConstraintOperator.NOT_IN):
            value = tuple(sorted(value, key=lambda item: str(item)))
        return ConstraintPlan(constraint.constraint_id, constraint.canonical_field, field, "profile", constraint.operator, value, polarity, True)

    def _translate(self, plan: ConstraintPlan) -> ConstraintPlan:
        if not plan.executable:
            return plan
        field, op, value = plan.projection_field, plan.operation, plan.value
        if op is ConstraintOperator.EQ: dsl = {"term": {field: value}}
        elif op is ConstraintOperator.NEQ: dsl = {"bool": {"must_not": [{"term": {field: value}}]}}
        elif op is ConstraintOperator.IN: dsl = {"terms": {field: list(value)}}
        elif op is ConstraintOperator.NOT_IN: dsl = {"bool": {"must_not": [{"terms": {field: list(value)}}]}}
        elif op in (ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT): dsl = {"range": {field: {op.value: value}}}
        elif op is ConstraintOperator.BETWEEN: dsl = {"range": {field: {"gte": value[0], "lte": value[1]}}}
        else: return ConstraintPlan(**{**plan.__dict__, "executable": False, "reason": "unsupported_operator"})
        if plan.polarity is ConstraintPolarity.EXCLUDED:
            dsl = {"bool": {"must_not": [dsl]}}
        return ConstraintPlan(**{**plan.__dict__, "dsl": dsl})
