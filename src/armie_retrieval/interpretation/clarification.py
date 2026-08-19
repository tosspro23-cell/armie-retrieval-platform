"""Deterministic clarification protocol foundation (Gate 3J).

This module is deliberately UI- and model-independent.  Clarifications are
unexecutable until resolved, and a resolved interpretation still requires
explicit confirmation and deterministic validation before any later runtime
integration may consume it.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from .models import CandidateInterpretation, InterpretationState

CLARIFICATION_ITEM_SCHEMA = "clarification-item-v1"
CLARIFICATION_RESOLUTION_SCHEMA = "clarification-resolution-v1"


class ClarificationStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class ClarificationType(str, Enum):
    REQUIREMENT_STRENGTH = "requirement_strength"
    EXCLUSION_SCOPE = "exclusion_scope"
    NUMERIC_INTENT = "numeric_intent"
    CATEGORY_ATTACHMENT = "category_attachment"
    UNSUPPORTED_INTENT = "unsupported_intent"
    REFERENCE_SCOPE = "reference_scope"


@dataclass(frozen=True)
class ClarificationItem:
    clarification_id: str
    request_id: str
    source_span: str
    surrounding_context: str
    current_interpretation_state: str
    ambiguity_type: ClarificationType
    allowed_resolutions: tuple[str, ...]
    question: str
    choices: tuple[str, ...] = ()
    provenance: tuple[dict[str, Any], ...] = ()
    depends_on: tuple[str, ...] = ()
    status: ClarificationStatus = ClarificationStatus.NEEDS_CLARIFICATION
    schema_version: str = CLARIFICATION_ITEM_SCHEMA


@dataclass(frozen=True)
class ClarificationResolution:
    clarification_id: str
    selected_resolution: str
    corrected_value: Any = None
    corrected_field: str | None = None
    user_text: str | None = None
    source: str = "user"
    sequence: int = 1
    schema_version: str = CLARIFICATION_RESOLUTION_SCHEMA


@dataclass(frozen=True)
class InterpretationSession:
    interpretation: CandidateInterpretation
    clarifications: tuple[ClarificationItem, ...] = ()
    resolutions: tuple[ClarificationResolution, ...] = ()
    confirmed: bool = False


def question_for(ambiguity_type: ClarificationType, source_span: str) -> tuple[str, tuple[str, ...]]:
    templates = {
        ClarificationType.REQUIREMENT_STRENGTH: (f"Should '{source_span}' be required, preferred, or context only?", ("REQUIRED", "PREFERRED", "CONTEXT_ONLY")),
        ClarificationType.EXCLUSION_SCOPE: (f"Should '{source_span}' exclude matching candidates, or remain contextual?", ("EXCLUDED", "CONTEXT_ONLY")),
        ClarificationType.NUMERIC_INTENT: (f"How should '{source_span}' be interpreted?", ("MINIMUM", "MAXIMUM", "EXACT", "APPROXIMATE", "REMOVE_FROM_CONSTRAINT_INTERPRETATION")),
        ClarificationType.CATEGORY_ATTACHMENT: (f"Is '{source_span}' a category requirement or contextual mention?", ("REQUIRED", "CONTEXT_ONLY")),
        ClarificationType.UNSUPPORTED_INTENT: (f"How should unsupported meaning '{source_span}' be handled?", ("ACKNOWLEDGE_UNSUPPORTED", "REMOVE_FROM_CONSTRAINT_INTERPRETATION")),
        ClarificationType.REFERENCE_SCOPE: (f"What does '{source_span}' refer to in this request?", ("REQUIRED", "PREFERRED", "CONTEXT_ONLY", "REMOVE_FROM_CONSTRAINT_INTERPRETATION")),
    }
    return templates[ambiguity_type]


def start_session(interpretation: CandidateInterpretation, clarifications: tuple[ClarificationItem, ...] = ()) -> InterpretationSession:
    state = InterpretationState.NEEDS_CLARIFICATION if any(c.status is ClarificationStatus.NEEDS_CLARIFICATION for c in clarifications) else InterpretationState.INTERPRETATION_COMPLETE
    return InterpretationSession(replace(interpretation, interpretation_state=state), clarifications)


def apply_resolution(session: InterpretationSession, resolution: ClarificationResolution, *, edit: bool = False) -> InterpretationSession:
    items = list(session.clarifications)
    index = next((i for i, item in enumerate(items) if item.clarification_id == resolution.clarification_id), None)
    if index is None:
        raise ValueError(f"unknown clarification_id: {resolution.clarification_id}")
    item = items[index]
    if item.status is ClarificationStatus.RESOLVED and not edit:
        raise ValueError("clarification is already resolved; use edit=True")
    if resolution.selected_resolution not in item.allowed_resolutions:
        raise ValueError("resolution is not allowed for this clarification")
    items[index] = replace(item, status=ClarificationStatus.CANCELLED if resolution.selected_resolution == "REMOVE_FROM_CONSTRAINT_INTERPRETATION" else ClarificationStatus.RESOLVED)
    resolutions = list(session.resolutions)
    resolutions.append(resolution)
    # Dependency invalidation is explicit and deterministic.
    if resolution.selected_resolution == "REMOVE_FROM_CONSTRAINT_INTERPRETATION":
        for i, other in enumerate(items):
            if resolution.clarification_id in other.depends_on:
                items[i] = replace(other, status=ClarificationStatus.CANCELLED)
    blocking = any(c.status is ClarificationStatus.NEEDS_CLARIFICATION for c in items)
    state = InterpretationState.NEEDS_CLARIFICATION if blocking else InterpretationState.INTERPRETATION_COMPLETE
    evidence = session.interpretation.evidence + ({"stage": "clarification", "clarification_id": resolution.clarification_id, "resolution": resolution.selected_resolution, "source": resolution.source, "sequence": resolution.sequence},)
    return replace(session, interpretation=replace(session.interpretation, interpretation_state=state, evidence=evidence), clarifications=tuple(items), resolutions=tuple(resolutions), confirmed=False)


def confirm(session: InterpretationSession) -> InterpretationSession:
    if any(c.status is ClarificationStatus.NEEDS_CLARIFICATION for c in session.clarifications):
        raise ValueError("blocking clarifications remain")
    return replace(session, interpretation=replace(session.interpretation, interpretation_state=InterpretationState.CONFIRMED), confirmed=True)


def validate_contract(session: InterpretationSession) -> InterpretationSession:
    if not session.confirmed:
        raise ValueError("final confirmation is required")
    errors = session.interpretation.validate()
    if errors:
        raise ValueError("invalid interpretation: " + "; ".join(errors))
    return replace(session, interpretation=replace(session.interpretation, interpretation_state=InterpretationState.VALIDATED_CONTRACT))
