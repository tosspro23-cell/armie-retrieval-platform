"""Gate 3F staged interpretation baseline.

The implementation deliberately stops at :class:`CandidateInterpretation`.
Span/role decomposition is explicit and deterministic mapping, normalization,
and validation are kept separate so failures can be attributed to a stage.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable

from armie_retrieval.constraints.registry import CANONICAL_VALUES, REGISTRY_ID, get_capability
from armie_retrieval.planners.ollama import OllamaPrerequisiteError, OllamaStructuredLLMClient

from .models import CandidateConstraint, CandidateInterpretation, InterpretationState, Polarity, SupportState

SPAN_SCHEMA = "constraint-span-v1"
ROLE_SCHEMA = "interpretation-role-v1"
MAPPING_SCHEMA = "registry-mapping-v1"
NORMALIZATION_SCHEMA = "constraint-normalization-v1"
STAGED_SCHEMA = "staged-interpretation-v1"


class SemanticRole(str, Enum):
    REQUIRED = "REQUIRED"
    EXCLUDED = "EXCLUDED"
    PREFERRED = "PREFERRED"
    CONTEXT_ONLY = "CONTEXT_ONLY"
    UNSUPPORTED = "UNSUPPORTED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class ConstraintSpan:
    span_id: str
    text: str
    start: int
    end: int
    normalized_surface: str
    schema_version: str = SPAN_SCHEMA


@dataclass(frozen=True)
class RoleAssignment:
    span_id: str
    role: SemanticRole
    confidence: str = "high"
    schema_version: str = ROLE_SCHEMA


@dataclass(frozen=True)
class MappingEvidence:
    span_id: str
    field: str | None
    canonical_value: Any = None
    support_state: SupportState = SupportState.SUPPORTED
    schema_version: str = MAPPING_SCHEMA


@dataclass(frozen=True)
class StagedResult:
    interpretation: CandidateInterpretation
    spans: tuple[ConstraintSpan, ...]
    roles: tuple[RoleAssignment, ...]
    mappings: tuple[MappingEvidence, ...]
    stage_errors: tuple[dict[str, Any], ...]
    metrics: dict[str, Any]
    latency_ms: float
    model_calls: int = 0
    schema_version: str = STAGED_SCHEMA


def _span(text: str, match: re.Match[str], index: int) -> ConstraintSpan:
    raw = match.group(0)
    return ConstraintSpan(f"s{index:03d}", raw, match.start(), match.end(), " ".join(raw.split()).lower())


def detect_spans(request: str) -> tuple[ConstraintSpan, ...]:
    """Stage 1: detect constraint-bearing phrases without assigning strength."""
    patterns = (
        r"(?:at least|no less than|more than|over|under|less than|exactly|around)\s+\d+\s+years?",
        r"\b\d+\s*\+\s*years?",
        r"between\s+\d+\s+and\s+\d+\s+years?",
        r"(?:must|required|only|prefer(?:ably)?|ideally)\s+(?:be\s+)?[^,;]+",
        r"(?:not necessarily|maybe|knowledge of)\s+[^,;]+",
        r"(?:roughly|around)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+years?",
        r"(?:preferably|ideally|bonus if|strong preference for)\s+[^,;]+",
        r"(?:experience working with|built systems for|has delivered|could be|delivered)\s+[^,;]+",
        r"[A-Za-z ]+\s+(?:required|preferred|only)\b",
        r"[A-Za-z ]+\s+or\s+[A-Za-z ]+\s+experience\b",
        r"\b(?:senior|principal)\s+[A-Za-z ]+",
        r"\b(?:healthcare|financial services|energy|retail|manufacturing|technology)\s+and\s+[A-Za-z ]+",
        r"[^,;]+\s+(?:required|preferred|would be ideal|would be a plus|bonus if)",
        r"(?:exclude|excluding|avoid|not from)\s+[^,;]+",
        r"\b(?:healthcare|financial services|energy|retail|manufacturing|technology)\s+experts?\s+only\b",
        r"(?:worked on|worked with|worked at|advised|delivered for|experience with)\s+[^,;]+",
        r"(?:in|based in|located in)\s+[A-Za-z][A-Za-z /-]+",
        r"\b(?:healthcare|financial services|energy|retail|manufacturing|technology)\b",
    )
    matches: list[re.Match[str]] = []
    for pattern in patterns:
        matches.extend(re.finditer(pattern, request, re.IGNORECASE))
    # Stable de-duplication; preserve nested spans rather than silently losing evidence.
    unique = {(m.start(), m.end(), m.group(0).lower()): m for m in matches}
    ordered = sorted(unique.values(), key=lambda m: (m.start(), -(m.end() - m.start())))
    return tuple(_span(request, match, i + 1) for i, match in enumerate(ordered))


def classify_roles(request: str, spans: Iterable[ConstraintSpan]) -> tuple[RoleAssignment, ...]:
    """Stage 2: classify semantic intent; registry terms alone never become HARD."""
    lower = request.lower()
    result: list[RoleAssignment] = []
    for span in spans:
        text = span.text.lower()
        before = lower[max(0, span.start - 40):span.start]
        if re.search(r"\b(?:around|roughly|maybe|not necessarily)\b", text):
            role = SemanticRole.AMBIGUOUS
        elif re.search(r"\b(?:exclude|excluding|avoid|must not|not from)\b", text) or re.search(r"\b(?:exclude|excluding|avoid|must not|not from)\b", before):
            role = SemanticRole.EXCLUDED
        elif re.search(r"\b(?:prefer|preferably|ideally|nice to have|bonus|preferred|would be a plus|would be ideal)\b", text) or re.search(r"\b(?:prefer|preferably|ideally|nice to have|bonus)\b", before):
            role = SemanticRole.PREFERRED
        elif re.search(r"\b(?:must|required|only|at least|no less than|more than|over|under|less than|exactly)\b", text) or re.search(r"\b(?:must|required|only)\b", before):
            role = SemanticRole.REQUIRED
        elif re.search(r"\b(?:worked on|worked with|experience with|experience working|knowledge of|in|based in|located in|advised|delivered for)\b", text):
            role = SemanticRole.CONTEXT_ONLY
        else:
            role = SemanticRole.CONTEXT_ONLY
        # Unsupported relationship/temporal semantics remain surfaced, never guessed.
        if re.search(r"\b(?:worked at|worked with|advised|delivered for|last|past)\b", text) and role not in {SemanticRole.REQUIRED, SemanticRole.EXCLUDED}:
            role = SemanticRole.UNSUPPORTED
        result.append(RoleAssignment(span.span_id, role))
    return tuple(result)


def map_registry(spans: Iterable[ConstraintSpan], roles: Iterable[RoleAssignment]) -> tuple[MappingEvidence, ...]:
    """Stage 3: map only REQUIRED/EXCLUDED spans to the authoritative registry."""
    by_id = {r.span_id: r for r in roles}
    spans_list = tuple(spans)
    result = []
    for span in spans:
        role = by_id[span.span_id].role
        if role not in {SemanticRole.REQUIRED, SemanticRole.EXCLUDED}:
            continue
        # A longer phrase owns its canonical token (e.g. ``excluding energy``);
        # do not emit duplicate predicates for nested detection spans.
        if any(other.span_id != span.span_id and other.start <= span.start and other.end >= span.end and (other.end - other.start) > (span.end - span.start) for other in spans_list):
            continue
        value = next((v for v in CANONICAL_VALUES["industry"] if v in span.normalized_surface), None)
        if value:
            result.append(MappingEvidence(span.span_id, "industry", value))
        elif re.search(r"\b(?:years?|year)\b|\+", span.normalized_surface):
            result.append(MappingEvidence(span.span_id, "years_experience"))
        elif "senior" in span.normalized_surface or "principal" in span.normalized_surface:
            result.append(MappingEvidence(span.span_id, "seniority"))
        elif "location" in span.normalized_surface or "based in" in span.normalized_surface:
            result.append(MappingEvidence(span.span_id, "location", support_state=SupportState.SUPPORTED))
        else:
            result.append(MappingEvidence(span.span_id, None, support_state=SupportState.UNRESOLVED))
    return tuple(result)


def normalize_mapping(span: ConstraintSpan, mapping: MappingEvidence, role: SemanticRole) -> CandidateConstraint | None:
    """Stage 4: deterministic operator/value normalization."""
    if mapping.field is None or mapping.support_state is not SupportState.SUPPORTED:
        return None
    text = span.normalized_surface
    if mapping.field == "industry":
        operator = "neq" if role is SemanticRole.EXCLUDED else "eq"
        return CandidateConstraint("industry", operator, mapping.canonical_value, mapping.canonical_value, Polarity.EXCLUSION if role is SemanticRole.EXCLUDED else Polarity.POSITIVE, "hard", source_span=span.text)
    m = re.search(r"(at least|no less than|more than|over|under|less than|exactly)\s+(\d+)", text)
    if m:
        op = {"at least": "gte", "no less than": "gte", "more than": "gt", "over": "gt", "under": "lt", "less than": "lt", "exactly": "eq"}[m.group(1)]
        return CandidateConstraint(mapping.field, op, int(m.group(2)), int(m.group(2)), source_span=span.text)
    m = re.search(r"(\d+)\s*\+", text)
    if m:
        return CandidateConstraint(mapping.field, "gte", int(m.group(1)), int(m.group(1)), source_span=span.text)
    if mapping.field == "seniority":
        value = "principal" if "principal" in text else "senior"
        return CandidateConstraint("seniority", "gte", value, value, source_span=span.text)
    return None


def validate_constraints(constraints: Iterable[CandidateConstraint]) -> tuple[tuple[CandidateConstraint, ...], tuple[dict[str, Any], ...]]:
    """Stage 5: validate registry/operator compatibility and contradictions."""
    accepted: list[CandidateConstraint] = []
    errors: list[dict[str, Any]] = []
    seen = set()
    for constraint in constraints:
        key = constraint.key()
        if key in seen:
            errors.append({"stage": "validation", "kind": "duplicate", "field": constraint.field})
            continue
        seen.add(key)
        capability = get_capability(constraint.field)
        if capability is None or constraint.operator not in {op.value for op in capability.operators}:
            errors.append({"stage": "validation", "kind": "unsupported_mapping", "field": constraint.field, "operator": constraint.operator})
            continue
        accepted.append(constraint)
    return tuple(accepted), tuple(errors)


def staged_extract(request: str, *, request_id: str = "dev-001") -> StagedResult:
    """Run the deterministic six-stage baseline and return non-executable output."""
    started = time.perf_counter()
    spans = detect_spans(request)
    roles = classify_roles(request, spans)
    mappings = map_registry(spans, roles)
    role_by_id = {item.span_id: item.role for item in roles}
    span_by_id = {item.span_id: item for item in spans}
    candidates = [normalize_mapping(span_by_id[m.span_id], m, role_by_id[m.span_id]) for m in mappings]
    normalized = [candidate for candidate in candidates if candidate is not None]
    valid, errors = validate_constraints(normalized)
    exclusions = tuple(c for c in valid if c.polarity is Polarity.EXCLUSION)
    hard = tuple(c for c in valid if c.polarity is Polarity.POSITIVE)
    unsupported = tuple(span.text for span, role in ((s, role_by_id[s.span_id]) for s in spans) if role is SemanticRole.UNSUPPORTED)
    unresolved = tuple(span.text for span, mapping in ((span_by_id[m.span_id], m) for m in mappings) if mapping.field is None)
    soft = tuple(CandidateConstraint("semantic_context", "eq", span.text, span.text, strength="soft", support_state=SupportState.UNRESOLVED, source_span=span.text) for span, role in ((s, role_by_id[s.span_id]) for s in spans) if role is SemanticRole.PREFERRED)
    context = tuple(span.text for span, role in ((s, role_by_id[s.span_id]) for s in spans) if role is SemanticRole.CONTEXT_ONLY)
    state = InterpretationState.PARTIALLY_SUPPORTED if unsupported or unresolved else (InterpretationState.NEEDS_CONFIRMATION if hard or exclusions else InterpretationState.NO_HARD_CONSTRAINTS)
    interpretation = CandidateInterpretation(request_id=request_id, natural_language_request=request, semantic_query=request, constraints=hard, exclusions=exclusions, soft_preferences=soft, unsupported_items=unsupported + context, unresolved_items=unresolved, interpretation_state=state, normalization={"arm": "deterministic-staged-v1", "schema_version": STAGED_SCHEMA}, evidence=tuple({"stage": "span", "span_id": s.span_id, "role": role_by_id[s.span_id].value, "source": s.text} for s in spans))
    return StagedResult(interpretation, spans, roles, mappings, errors, {"span_count": len(spans), "required_count": sum(r.role is SemanticRole.REQUIRED for r in roles), "excluded_count": sum(r.role is SemanticRole.EXCLUDED for r in roles), "context_only_count": sum(r.role is SemanticRole.CONTEXT_ONLY for r in roles), "preferred_count": sum(r.role is SemanticRole.PREFERRED for r in roles)}, (time.perf_counter() - started) * 1000)


class ModelAssistedStagedExtractor:
    """Optional narrow model arm: spans/roles only, deterministic downstream stages."""

    identity = "staged-qwen3-4b-span-role-v1"
    prompt_fingerprint = "gate3f-span-role-v1"

    def __init__(self, model: str = "qwen3:4b", *, base_url: str = "http://127.0.0.1:11434", timeout_seconds: float = 90.0):
        self.model = model
        self.client = OllamaStructuredLLMClient(model, base_url=base_url, timeout_seconds=timeout_seconds)

    def extract(self, request: str, *, request_id: str = "dev-model-001") -> StagedResult:
        started = time.perf_counter()
        try:
            payload = self.client.complete(prompt=(
                "Return JSON only with spans [{text,start,end,role}] where role is "
                "REQUIRED, EXCLUDED, PREFERRED, CONTEXT_ONLY, UNSUPPORTED, or AMBIGUOUS. "
                "Do not map fields or operators. Never infer REQUIRED from a registry term.\n"
                f"Request: {request}"
            ))
            raw = payload.get("spans", []) if isinstance(payload, dict) else []
            spans = tuple(ConstraintSpan(f"m{i:03d}", str(item["text"]), int(item.get("start", 0)), int(item.get("end", 0)), " ".join(str(item["text"]).split()).lower()) for i, item in enumerate(raw, 1))
            roles = tuple(RoleAssignment(span.span_id, SemanticRole(str(raw[i].get("role", "AMBIGUOUS")).upper())) for i, span in enumerate(spans))
            mappings = map_registry(spans, roles)
            role_by_id, span_by_id = {r.span_id: r.role for r in roles}, {s.span_id: s for s in spans}
            normalized = [normalize_mapping(span_by_id[m.span_id], m, role_by_id[m.span_id]) for m in mappings]
            valid, errors = validate_constraints(c for c in normalized if c is not None)
            interpretation = CandidateInterpretation(request_id=request_id, natural_language_request=request, semantic_query=request, constraints=tuple(c for c in valid if c.polarity is Polarity.POSITIVE), exclusions=tuple(c for c in valid if c.polarity is Polarity.EXCLUSION), normalization={"arm": self.identity, "model": self.model}, interpretation_state=InterpretationState.NEEDS_CONFIRMATION if valid else InterpretationState.NO_HARD_CONSTRAINTS, evidence=tuple({"stage": "span", "span_id": s.span_id, "role": role_by_id[s.span_id].value, "source": s.text} for s in spans))
            return StagedResult(interpretation, spans, roles, mappings, errors, {"model": self.model, "model_calls": 1}, (time.perf_counter() - started) * 1000, model_calls=1)
        except (OllamaPrerequisiteError, RuntimeError, ValueError, KeyError) as exc:
            fallback = staged_extract(request, request_id=request_id)
            return StagedResult(fallback.interpretation, fallback.spans, fallback.roles, fallback.mappings, fallback.stage_errors + ({"stage": "model", "kind": "not_run", "error": str(exc)},), {**fallback.metrics, "model": self.model, "model_calls": 0, "fallback": "deterministic-staged-v1"}, (time.perf_counter() - started) * 1000, model_calls=0)
