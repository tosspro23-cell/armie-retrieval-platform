"""Backend-independent semantic contracts for v0.5 constraint-aware retrieval.

Gate 1 deliberately stops at types and deterministic validation.  This module
does not know about Elasticsearch, indexes, SDKs, planners, or runtime
execution.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from enum import Enum
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ConstraintOperator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    IN = "in"
    NOT_IN = "not_in"
    GTE = "gte"
    GT = "gt"
    LTE = "lte"
    LT = "lt"
    BETWEEN = "between"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"


class ConstraintCategory(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    ROLE = "role"
    SENIORITY = "seniority"
    TEMPORAL = "temporal"
    NEGATIVE = "negative"
    RELATIONSHIP = "relationship"


class ConstraintStrength(str, Enum):
    HARD = "hard"
    SOFT = "soft"


class ConstraintState(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    UNKNOWN = "UNKNOWN"


class ValidationState(str, Enum):
    VALID = "VALID"
    INVALID_CONTRACT = "INVALID_CONTRACT"
    UNSUPPORTED_CONSTRAINT = "UNSUPPORTED_CONSTRAINT"
    AMBIGUOUS_CONSTRAINT = "AMBIGUOUS_CONSTRAINT"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    INVALID_OPERATOR = "INVALID_OPERATOR"
    CONTRADICTION = "CONTRADICTION"


class TemporalOperator(str, Enum):
    AFTER = "after"
    BEFORE = "before"
    BETWEEN = "between"


class RelationshipType(str, Enum):
    WORKED_AT = "worked_at"
    DELIVERED_FOR = "delivered_for"
    ADVISED = "advised"
    MANAGED = "managed"
    PARTNERED_WITH = "partnered_with"


class ConstraintPolicy(ContractModel):
    mode: Literal["strict"] = "strict"
    unknown_hard_constraint: Literal["exclude"] = "exclude"
    silent_relaxation: Literal[False] = False


class FieldSpec(ContractModel):
    name: str
    semantic_type: ConstraintCategory
    allowed_operators: tuple[ConstraintOperator, ...]
    nullable: bool = True
    evidence_capable: bool = False


class CanonicalFieldRegistry:
    """Small Gate 1 field registry; it is not a Dataset ontology."""

    _fields: ClassVar[dict[str, FieldSpec]] = {
        "years_experience": FieldSpec(name="years_experience", semantic_type=ConstraintCategory.NUMERIC, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT, ConstraintOperator.BETWEEN)),
        "industry": FieldSpec(name="industry", semantic_type=ConstraintCategory.CATEGORICAL, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS)),
        "location": FieldSpec(name="location", semantic_type=ConstraintCategory.CATEGORICAL, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS)),
        "discipline": FieldSpec(name="discipline", semantic_type=ConstraintCategory.CATEGORICAL, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS)),
        "role": FieldSpec(name="role", semantic_type=ConstraintCategory.ROLE, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS)),
        "seniority": FieldSpec(name="seniority", semantic_type=ConstraintCategory.SENIORITY, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT)),
        "capability": FieldSpec(name="capability", semantic_type=ConstraintCategory.CATEGORICAL, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS)),
        "prohibited_capability": FieldSpec(name="prohibited_capability", semantic_type=ConstraintCategory.NEGATIVE, allowed_operators=(ConstraintOperator.EQ, ConstraintOperator.NEQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS)),
        "start_date": FieldSpec(name="start_date", semantic_type=ConstraintCategory.TEMPORAL, allowed_operators=(ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT, ConstraintOperator.BETWEEN)),
        "end_date": FieldSpec(name="end_date", semantic_type=ConstraintCategory.TEMPORAL, allowed_operators=(ConstraintOperator.GTE, ConstraintOperator.GT, ConstraintOperator.LTE, ConstraintOperator.LT, ConstraintOperator.BETWEEN)),
    }

    @classmethod
    def get(cls, field: str) -> FieldSpec | None:
        return cls._fields.get(field)

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(sorted(cls._fields))


class Constraint(ContractModel):
    constraint_id: str | None = None
    canonical_field: str
    operator: ConstraintOperator
    expected_value: Any
    category: ConstraintCategory
    strength: ConstraintStrength = ConstraintStrength.HARD
    provenance: str | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "Constraint":
        if not self.canonical_field.strip():
            raise ValueError("canonical_field cannot be empty")
        if self.strength is ConstraintStrength.SOFT and self.category is ConstraintCategory.NEGATIVE:
            raise ValueError("negative/prohibited constraints must be hard")
        if self.operator in (ConstraintOperator.IN, ConstraintOperator.NOT_IN):
            if not isinstance(self.expected_value, (list, tuple, set, frozenset)) or not self.expected_value:
                raise ValueError(f"{self.operator.value} requires a non-empty collection")
        elif self.operator is ConstraintOperator.BETWEEN:
            if not isinstance(self.expected_value, (list, tuple)) or len(self.expected_value) != 2:
                raise ValueError("between requires exactly two ordered bounds")
            if self.expected_value[0] > self.expected_value[1]:
                raise ValueError("between lower bound must not exceed upper bound")
        elif self.operator in (ConstraintOperator.CONTAINS, ConstraintOperator.NOT_CONTAINS):
            if not isinstance(self.expected_value, str) or not self.expected_value.strip():
                raise ValueError(f"{self.operator.value} requires a non-empty string")
        else:
            if isinstance(self.expected_value, (list, tuple, set, frozenset, dict)):
                raise ValueError(f"{self.operator.value} expects one comparable value")
        if self.constraint_id is None:
            payload = {"field": self.canonical_field, "operator": self.operator.value, "value": _identity_value(self.expected_value, self.operator), "category": self.category.value, "strength": self.strength.value}
            digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
            object.__setattr__(self, "constraint_id", f"constraint-{digest}")
        return self


class TemporalConstraint(ContractModel):
    constraint_id: str | None = None
    operator: TemporalOperator
    start: date | None = None
    end: date | None = None
    strength: ConstraintStrength = ConstraintStrength.HARD
    provenance: str | None = None

    @model_validator(mode="after")
    def validate_range(self) -> "TemporalConstraint":
        if self.operator is TemporalOperator.AFTER and self.start is None:
            raise ValueError("temporal after requires a start bound")
        if self.operator is TemporalOperator.BEFORE and self.end is None:
            raise ValueError("temporal before requires an end bound")
        if self.operator is TemporalOperator.BETWEEN and (self.start is None or self.end is None):
            raise ValueError("temporal between requires start and end")
        if self.start and self.end and self.start > self.end:
            raise ValueError("temporal start must not exceed end")
        if self.constraint_id is None:
            value = f"{self.operator.value}:{self.start}:{self.end}:{self.strength.value}"
            object.__setattr__(self, "constraint_id", "temporal-" + hashlib.sha256(value.encode()).hexdigest()[:16])
        return self


class RelationshipConstraint(ContractModel):
    constraint_id: str | None = None
    relation: RelationshipType
    object: str
    subject_type: str = "expert"
    object_type: str = "organization_or_project"
    start: date | None = None
    end: date | None = None
    strength: ConstraintStrength = ConstraintStrength.HARD
    evidence_reference: str | None = None
    provenance: str | None = None

    @model_validator(mode="after")
    def validate_relationship(self) -> "RelationshipConstraint":
        if not self.object.strip():
            raise ValueError("relationship object cannot be empty")
        if self.start and self.end and self.start > self.end:
            raise ValueError("relationship start must not exceed end")
        if self.constraint_id is None:
            value = json.dumps({"relation": self.relation.value, "object": self.object, "start": str(self.start), "end": str(self.end), "strength": self.strength.value}, sort_keys=True)
            object.__setattr__(self, "constraint_id", "relationship-" + hashlib.sha256(value.encode()).hexdigest()[:16])
        return self


class UnsupportedConstraint(ContractModel):
    expression: str
    reason: str
    provenance: str | None = None

    @model_validator(mode="after")
    def validate_expression(self) -> "UnsupportedConstraint":
        if not self.expression.strip():
            raise ValueError("unsupported constraint expression cannot be empty")
        if not self.reason.strip():
            raise ValueError("unsupported constraint reason cannot be empty")
        return self


class CandidateConstraintResult(ContractModel):
    constraint_id: str
    status: ConstraintState
    canonical_field: str | None = None
    expected_operator: ConstraintOperator | None = None
    expected_value: Any = None
    observed_value: Any = None
    evidence: tuple[str, ...] = ()
    source: str | None = None
    reason_code: str | None = None


class RetrievalContract(ContractModel):
    semantic_query: str
    hard_constraints: tuple[Constraint, ...] = ()
    soft_preferences: tuple[Constraint, ...] = ()
    exclusions: tuple[Constraint, ...] = ()
    temporal_constraints: tuple[TemporalConstraint, ...] = ()
    relationship_constraints: tuple[RelationshipConstraint, ...] = ()
    unsupported_constraints: tuple[UnsupportedConstraint, ...] = ()
    policy: ConstraintPolicy = Field(default_factory=ConstraintPolicy)
    contract_id: str | None = None
    contract_version: str = "v0.5.0-contract-1"

    @model_validator(mode="after")
    def validate_strengths(self) -> "RetrievalContract":
        if not self.semantic_query.strip():
            raise ValueError("semantic_query cannot be empty")
        if any(c.strength is not ConstraintStrength.HARD for c in self.hard_constraints):
            raise ValueError("hard_constraints must contain only hard constraints")
        if any(c.strength is not ConstraintStrength.SOFT for c in self.soft_preferences):
            raise ValueError("soft_preferences must contain only soft constraints")
        if any(c.strength is not ConstraintStrength.HARD for c in self.exclusions):
            raise ValueError("exclusions must contain only hard constraints")
        if self.contract_id is None:
            payload = _identity_value(self.model_dump(mode="json", exclude={"contract_id"}))
            digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]
            object.__setattr__(self, "contract_id", f"contract-{digest}")
        return self


class ValidationIssue(ContractModel):
    state: ValidationState
    message: str
    constraint_id: str | None = None
    reason_code: str


class ContractValidation(ContractModel):
    state: ValidationState
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def valid(self) -> bool:
        return self.state is ValidationState.VALID


def validate_contract(contract: RetrievalContract, registry: type[CanonicalFieldRegistry] = CanonicalFieldRegistry) -> ContractValidation:
    """Run bounded deterministic field/operator and contradiction validation."""
    issues: list[ValidationIssue] = []
    constraints = (*contract.hard_constraints, *contract.soft_preferences, *contract.exclusions)
    for constraint in constraints:
        spec = registry.get(constraint.canonical_field)
        if spec is None:
            issues.append(ValidationIssue(state=ValidationState.UNSUPPORTED_CONSTRAINT, message=f"unsupported canonical field: {constraint.canonical_field}", constraint_id=constraint.constraint_id, reason_code="unsupported_field"))
            continue
        if constraint.operator not in spec.allowed_operators:
            issues.append(ValidationIssue(state=ValidationState.INVALID_OPERATOR, message=f"operator {constraint.operator.value} is not allowed for {constraint.canonical_field}", constraint_id=constraint.constraint_id, reason_code="operator_not_allowed"))
        if not _value_compatible(constraint, spec):
            issues.append(ValidationIssue(state=ValidationState.TYPE_MISMATCH, message=f"value is incompatible with {spec.semantic_type.value} field {spec.name}", constraint_id=constraint.constraint_id, reason_code="value_type_mismatch"))
        if constraint.category is not spec.semantic_type:
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message=f"category {constraint.category.value} does not match registry category {spec.semantic_type.value} for {spec.name}", constraint_id=constraint.constraint_id, reason_code="field_category_mismatch"))
    for temporal in contract.temporal_constraints:
        if temporal.operator is TemporalOperator.AFTER and temporal.start is None:
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message="temporal after requires a start bound", constraint_id=temporal.constraint_id, reason_code="temporal_bound_missing"))
        if temporal.operator is TemporalOperator.BEFORE and temporal.end is None:
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message="temporal before requires an end bound", constraint_id=temporal.constraint_id, reason_code="temporal_bound_missing"))
        if temporal.operator is TemporalOperator.BETWEEN and (temporal.start is None or temporal.end is None):
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message="temporal between requires start and end", constraint_id=temporal.constraint_id, reason_code="temporal_bound_missing"))
        if temporal.start and temporal.end and temporal.start > temporal.end:
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message="temporal start must not exceed end", constraint_id=temporal.constraint_id, reason_code="temporal_interval_invalid"))
    for relationship in contract.relationship_constraints:
        if not relationship.object.strip():
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message="relationship object cannot be empty", constraint_id=relationship.constraint_id, reason_code="relationship_object_missing"))
        if relationship.start and relationship.end and relationship.start > relationship.end:
            issues.append(ValidationIssue(state=ValidationState.INVALID_CONTRACT, message="relationship start must not exceed end", constraint_id=relationship.constraint_id, reason_code="relationship_interval_invalid"))
    for unsupported in contract.unsupported_constraints:
        issues.append(ValidationIssue(state=ValidationState.UNSUPPORTED_CONSTRAINT, message=f"unsupported structured requirement: {unsupported.expression} ({unsupported.reason})", reason_code="unsupported_requirement"))
    # Exclusions have opposite polarity and must not be treated as competing
    # positive equalities (e.g. require Energy + exclude Banking).
    issues.extend(_contradictions((*contract.hard_constraints, *contract.soft_preferences)))
    if issues:
        state = ValidationState.CONTRADICTION if any(i.state is ValidationState.CONTRADICTION for i in issues) else issues[0].state
        return ContractValidation(state=state, issues=tuple(issues))
    return ContractValidation(state=ValidationState.VALID)


def _value_compatible(constraint: Constraint, spec: FieldSpec) -> bool:
    values = constraint.expected_value if constraint.operator in (ConstraintOperator.IN, ConstraintOperator.NOT_IN, ConstraintOperator.BETWEEN) else (constraint.expected_value,)
    if constraint.operator is ConstraintOperator.BETWEEN and not isinstance(constraint.expected_value, (list, tuple)):
        return False
    if spec.semantic_type is ConstraintCategory.NUMERIC:
        return all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)
    if spec.semantic_type is ConstraintCategory.TEMPORAL:
        return all(isinstance(v, (date, datetime, str)) for v in values)
    return all(isinstance(v, (str, int, float, bool)) for v in values)


def _contradictions(constraints: tuple[Constraint, ...] | list[Constraint]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    grouped: dict[str, list[Constraint]] = {}
    for constraint in constraints:
        if constraint.strength is ConstraintStrength.HARD:
            grouped.setdefault(constraint.canonical_field, []).append(constraint)
    for field, values in grouped.items():
        equals = {_stable_key(c.expected_value) for c in values if c.operator is ConstraintOperator.EQ}
        not_equals = {_stable_key(c.expected_value) for c in values if c.operator is ConstraintOperator.NEQ}
        included = {_stable_key(item) for c in values if c.operator is ConstraintOperator.IN for item in c.expected_value}
        excluded = {_stable_key(item) for c in values if c.operator is ConstraintOperator.NOT_IN for item in c.expected_value}
        if len(equals) > 1 or equals & not_equals or included & excluded or (included and included <= excluded):
            issues.append(ValidationIssue(state=ValidationState.CONTRADICTION, message=f"conflicting categorical constraints for {field}", reason_code="categorical_contradiction"))
        lower_values = [(c.expected_value, c.operator) for c in values if c.operator in (ConstraintOperator.GTE, ConstraintOperator.GT) and isinstance(c.expected_value, (int, float)) and not isinstance(c.expected_value, bool)]
        upper_values = [(c.expected_value, c.operator) for c in values if c.operator in (ConstraintOperator.LTE, ConstraintOperator.LT) and isinstance(c.expected_value, (int, float)) and not isinstance(c.expected_value, bool)]
        lower = None
        if lower_values:
            lower_value = max(item[0] for item in lower_values)
            lower = (lower_value, any(value == lower_value and operator is ConstraintOperator.GT for value, operator in lower_values))
        upper = None
        if upper_values:
            upper_value = min(item[0] for item in upper_values)
            upper = (upper_value, any(value == upper_value and operator is ConstraintOperator.LT for value, operator in upper_values))
        if lower and upper and (lower[0] > upper[0] or (lower[0] == upper[0] and (lower[1] or upper[1]))):
            issues.append(ValidationIssue(state=ValidationState.CONTRADICTION, message=f"impossible ordered interval for {field}", reason_code="numeric_interval_contradiction"))
    return issues


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (set, frozenset, tuple)):
        return [_json_value(v) for v in value]
    if isinstance(value, list):
        return [_json_value(v) for v in value]
    return value


def _identity_value(value: Any, operator: ConstraintOperator | None = None) -> Any:
    """Canonicalize values for semantic IDs without reordering ordered ranges."""
    if operator in (ConstraintOperator.IN, ConstraintOperator.NOT_IN) and isinstance(value, (list, tuple, set, frozenset)):
        return sorted((_identity_value(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), default=str))
    if isinstance(value, dict):
        return {key: _identity_value(value[key]) for key in sorted(value)}
    if isinstance(value, (set, frozenset)):
        return sorted((_identity_value(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), default=str))
    if isinstance(value, (list, tuple)):
        return [_identity_value(item) for item in value]
    return _json_value(value)


def _stable_key(value: Any) -> str:
    return json.dumps(_json_value(value), sort_keys=True, separators=(",", ":"), default=str)


# Short aliases keep the public vocabulary ergonomic without introducing a
# second type system.
Operator = ConstraintOperator
ConstraintKind = ConstraintCategory
ConstraintStatus = ConstraintState
ContractStatus = ValidationState


__all__ = ["CandidateConstraintResult", "CanonicalFieldRegistry", "Constraint", "ConstraintCategory", "ConstraintKind", "ConstraintOperator", "ConstraintPolicy", "ConstraintState", "ConstraintStatus", "ConstraintStrength", "ContractStatus", "ContractValidation", "FieldSpec", "Operator", "RelationshipConstraint", "RelationshipType", "RetrievalContract", "TemporalConstraint", "TemporalOperator", "UnsupportedConstraint", "ValidationIssue", "ValidationState", "validate_contract"]
