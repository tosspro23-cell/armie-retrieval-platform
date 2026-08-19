"""Versioned, non-executable candidate interpretation contract.

The types in this module deliberately do not inherit from ``RetrievalContract``
and expose no method that executes or compiles a candidate.  They are the
stable Gate 1 interchange surface for future extractor arms.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from armie_retrieval.constraints.registry import REGISTRY_ID, get_capability

CANDIDATE_INTERPRETATION_SCHEMA = "nl-constraint-interpretation-v1"


class InterpretationState(str, Enum):
    INTERPRETED = "INTERPRETED"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    AMBIGUOUS = "AMBIGUOUS"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTORY = "CONTRADICTORY"
    NO_HARD_CONSTRAINTS = "NO_HARD_CONSTRAINTS"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    INTERPRETATION_COMPLETE = "INTERPRETATION_COMPLETE"
    CONFIRMED = "CONFIRMED"
    VALIDATED_CONTRACT = "VALIDATED_CONTRACT"


class Polarity(str, Enum):
    POSITIVE = "positive"
    EXCLUSION = "exclusion"


class SupportState(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNRESOLVED = "unresolved"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class CandidateConstraint:
    field: str
    operator: str
    raw_value: Any
    normalized_value: Any = None
    polarity: Polarity = Polarity.POSITIVE
    strength: str = "hard"
    support_state: SupportState = SupportState.SUPPORTED
    ambiguity_state: str | None = None
    source_span: str | None = None
    rationale: str | None = None

    def key(self) -> tuple[str, str, str, str, str]:
        """Return a deterministic comparison key for evaluator matching."""
        import json

        value = self.normalized_value if self.normalized_value is not None else self.raw_value
        return (
            self.field,
            self.operator,
            json.dumps(value, sort_keys=True, separators=(",", ":")),
            self.polarity.value,
            self.strength,
        )

    def validate_against_registry(self) -> list[str]:
        errors: list[str] = []
        capability = get_capability(self.field)
        if self.support_state is SupportState.SUPPORTED and capability is None:
            errors.append(f"unsupported registry field: {self.field}")
        if capability is not None and self.operator not in {op.value for op in capability.operators}:
            errors.append(f"operator {self.operator!r} is not supported for {self.field}")
        if self.polarity is Polarity.EXCLUSION and self.strength != "hard":
            errors.append("exclusions must be hard")
        if self.strength not in {"hard", "soft"}:
            errors.append(f"invalid strength: {self.strength}")
        return errors


@dataclass(frozen=True)
class CandidateInterpretation:
    request_id: str
    natural_language_request: str
    semantic_query: str
    constraints: tuple[CandidateConstraint, ...] = ()
    exclusions: tuple[CandidateConstraint, ...] = ()
    soft_preferences: tuple[CandidateConstraint, ...] = ()
    unsupported_items: tuple[str, ...] = ()
    unresolved_items: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    interpretation_state: InterpretationState = InterpretationState.NO_HARD_CONSTRAINTS
    registry_id: str = REGISTRY_ID
    normalization: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[dict[str, Any], ...] = ()
    schema_version: str = CANDIDATE_INTERPRETATION_SCHEMA

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.schema_version != CANDIDATE_INTERPRETATION_SCHEMA:
            errors.append(f"schema_version must be {CANDIDATE_INTERPRETATION_SCHEMA}")
        if not self.request_id.strip() or not self.natural_language_request.strip():
            errors.append("request_id and natural_language_request are required")
        if self.registry_id != REGISTRY_ID:
            errors.append(f"registry_id must be {REGISTRY_ID}")
        all_constraints = self.constraints + self.exclusions + self.soft_preferences
        for constraint in all_constraints:
            errors.extend(constraint.validate_against_registry())
        for constraint in self.exclusions:
            if constraint.polarity is not Polarity.EXCLUSION:
                errors.append("exclusions must use exclusion polarity")
        if self.contradictions and self.interpretation_state is not InterpretationState.CONTRADICTORY:
            errors.append("contradictions require CONTRADICTORY state")
        if self.interpretation_state is InterpretationState.NO_HARD_CONSTRAINTS and self.constraints:
            errors.append("NO_HARD_CONSTRAINTS cannot contain candidate HARD constraints")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
