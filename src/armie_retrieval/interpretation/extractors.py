"""Gate 2 bounded extraction baselines.

These arms stop at ``CandidateInterpretation``. They never compile or execute
retrieval contracts. The rule arm is intentionally conservative; the Ollama arm
is optional and always passes through deterministic schema validation.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from armie_retrieval.constraints.registry import REGISTRY_ID, CANONICAL_VALUES
from armie_retrieval.planners.ollama import OllamaPrerequisiteError, OllamaStructuredLLMClient

from .models import CandidateConstraint, CandidateInterpretation, InterpretationState, Polarity, SupportState


class InterpretationExtractor(Protocol):
    identity: str

    def extract(self, natural_language_request: str, *, request_id: str) -> "ExtractionResult": ...


@dataclass(frozen=True)
class ExtractionResult:
    interpretation: CandidateInterpretation | None
    arm: str
    status: str
    latency_ms: float
    metadata: Mapping[str, Any]
    error: str | None = None


def _constraint(field: str, operator: str, raw: Any, *, normalized: Any = None, strength: str = "hard", polarity: Polarity = Polarity.POSITIVE, support: SupportState = SupportState.SUPPORTED, source: str | None = None) -> CandidateConstraint:
    return CandidateConstraint(field, operator, raw, normalized if normalized is not None else raw, polarity, strength, support, source_span=source)


def _state(constraints, exclusions, soft, unsupported, unresolved, contradictions):
    if contradictions:
        return InterpretationState.CONTRADICTORY
    if unresolved:
        return InterpretationState.AMBIGUOUS
    if constraints or exclusions:
        return InterpretationState.PARTIALLY_SUPPORTED if unsupported else InterpretationState.NEEDS_CONFIRMATION
    if unsupported:
        return InterpretationState.UNSUPPORTED
    if soft:
        return InterpretationState.NO_HARD_CONSTRAINTS
    return InterpretationState.NO_HARD_CONSTRAINTS


class RuleExtractor:
    identity = "rule-baseline-v1"

    def extract(self, natural_language_request: str, *, request_id: str) -> ExtractionResult:
        started = time.perf_counter()
        text = natural_language_request.strip()
        lower = text.lower()
        constraints: list[CandidateConstraint] = []
        exclusions: list[CandidateConstraint] = []
        soft: list[CandidateConstraint] = []
        unsupported: list[str] = []
        unresolved: list[str] = []
        contradictions: list[str] = []

        # Explicit unsupported semantics are retained rather than dropped.
        for phrase in (r"(?:last|past)\s+\w+\s+years?", r"delivered\s+(?:projects?\s+)?for\s+[A-Z][\w-]*", r"worked\s+(?:at|with)\s+[A-Z][\w-]*", r"advised\s+[A-Z][\w-]*"):
            for match in re.finditer(phrase, text, re.IGNORECASE):
                unsupported.append(match.group(0))

        # Numeric operators: only explicit, supported expressions become HARD.
        for match in re.finditer(r"(?:at\s+least|no\s+less\s+than|more\s+than|over|under|less\s+than|exactly)\s+(\d+)\s*(?:years?)?", lower):
            phrase, number = match.group(0), int(match.group(1))
            op = "gte" if phrase.startswith(("at least", "no less")) else "gt" if phrase.startswith(("more", "over")) else "lt" if phrase.startswith(("under", "less")) else "eq"
            constraints.append(_constraint("years_experience", op, number, source=phrase))
        for match in re.finditer(r"(\d+)\s*\+\s*years?", lower):
            constraints.append(_constraint("years_experience", "gte", int(match.group(1)), source=match.group(0)))
        for match in re.finditer(r"between\s+(\d+)\s+and\s+(\d+)\s+years?", lower):
            constraints.append(_constraint("years_experience", "between", [int(match.group(1)), int(match.group(2))], source=match.group(0)))
        for match in re.finditer(r"around\s+(\d+)\s+years?", lower):
            unresolved.append(match.group(0))

        # Canonical industry values are drawn from the authoritative registry.
        for industry in CANONICAL_VALUES["industry"]:
            if re.search(rf"\b{re.escape(industry)}\b", lower):
                before = lower[max(0, lower.find(industry) - 35):lower.find(industry)]
                if re.search(r"excluding|not from|must not|avoid", before):
                    exclusions.append(_constraint("industry", "neq", industry, polarity=Polarity.EXCLUSION, source=industry))
                elif re.search(r"only|required|must|in\s*$|experts?\s*$", before) or re.search(rf"{re.escape(industry)}\s+experts?", lower):
                    constraints.append(_constraint("industry", "eq", industry, source=industry))
                else:
                    unresolved.append(industry)

        # Simple, explicit role/seniority/location patterns.
        if re.search(r"\b(principal)\b", lower):
            constraints.append(_constraint("seniority", "gte", "principal", source="principal"))
        elif re.search(r"\bsenior(?:-level|\s+level)?\b", lower) and not re.search(r"prefer|ideally|bonus|nice", lower):
            constraints.append(_constraint("seniority", "gte", "senior", source="senior"))
        if re.search(r"search\s*/?\s*retrieval\s+engineer", lower) and re.search(r"required|must|only", lower):
            constraints.append(_constraint("role", "eq", "search / retrieval engineer", source="Search / Retrieval Engineer"))
        location = re.search(r"based\s+in\s+([A-Za-z][A-Za-z ]+)", text, re.IGNORECASE)
        if location and re.search(r"must|required|only", lower):
            constraints.append(_constraint("location", "eq", location.group(1).strip().lower(), source=location.group(0)))

        # Preference language stays SOFT or semantic-only.
        if re.search(r"prefer(?:ably)?|ideally|nice to have|bonus", lower):
            if "senior" in lower:
                soft.append(_constraint("seniority", "gte", "senior", strength="soft", source="preference language"))
            # Capability is semantic intent in the current C1 registry, not a
            # structured supported field. Preserve the phrase in semantic_query
            # rather than inventing a second capability vocabulary.

        if re.search(r"at least\s+20.*under\s+10|under\s+10.*at least\s+20", lower):
            contradictions.append("years_experience >= 20 conflicts with years_experience < 10")
        if "only" in lower and "excluding" in lower:
            for industry in CANONICAL_VALUES["industry"]:
                if f"only {industry}" in lower and f"excluding {industry}" in lower:
                    contradictions.append(f"industry = {industry} conflicts with industry != {industry}")

        state = _state(constraints, exclusions, soft, unsupported, unresolved, contradictions)
        interpretation = CandidateInterpretation(
            request_id=request_id,
            natural_language_request=text,
            semantic_query=text,
            constraints=tuple(constraints),
            exclusions=tuple(exclusions),
            soft_preferences=tuple(soft),
            unsupported_items=tuple(unsupported),
            unresolved_items=tuple(unresolved),
            contradictions=tuple(contradictions),
            interpretation_state=state,
            normalization={"arm": self.identity},
            evidence=tuple({"source": c.source_span, "field": c.field} for c in constraints + exclusions + soft if c.source_span),
        )
        errors = interpretation.validate()
        elapsed = (time.perf_counter() - started) * 1000
        if errors:
            return ExtractionResult(None, self.identity, "INVALID_OUTPUT", elapsed, {"errors": errors})
        return ExtractionResult(interpretation, self.identity, "COMPLETED", elapsed, {"registry_id": REGISTRY_ID})


class OllamaStructuredExtractor:
    identity = "ollama-structured-qwen3-4b-v1"
    prompt_fingerprint = "gate3-structured-v1"

    def __init__(self, model: str = "qwen3:4b", *, base_url: str = "http://127.0.0.1:11434", timeout_seconds: float = 90.0):
        self.model = model
        self.client = OllamaStructuredLLMClient(model, base_url=base_url, timeout_seconds=timeout_seconds)

    def extract(self, natural_language_request: str, *, request_id: str) -> ExtractionResult:
        started = time.perf_counter()
        try:
            payload = self.client.complete(prompt=self._prompt(natural_language_request))
            interpretation = self._parse(payload, natural_language_request, request_id)
            errors = interpretation.validate()
            if errors:
                raise ValueError("; ".join(errors))
            return ExtractionResult(interpretation, self.identity, "COMPLETED", (time.perf_counter() - started) * 1000, {"model": self.model, "temperature": 0, "structured_output": True, "registry_id": REGISTRY_ID})
        except OllamaPrerequisiteError as exc:
            return ExtractionResult(None, self.identity, "NOT_RUN", (time.perf_counter() - started) * 1000, {"model": self.model}, str(exc))
        except RuntimeError as exc:
            return ExtractionResult(None, self.identity, "NOT_RUN", (time.perf_counter() - started) * 1000, {"model": self.model}, f"structured model call unavailable: {exc}")
        except Exception as exc:  # model output is untrusted
            return ExtractionResult(None, self.identity, "INVALID_OUTPUT", (time.perf_counter() - started) * 1000, {"model": self.model}, str(exc))

    def _prompt(self, request: str) -> str:
        return json.dumps({"task": "Return a candidate interpretation only; never execute retrieval.", "request": request, "registry_id": REGISTRY_ID, "supported_fields": ["industry", "role", "location", "years_experience", "seniority"], "output": {"semantic_query": "string", "constraints": [], "exclusions": [], "soft_preferences": [], "unsupported_items": [], "unresolved_items": [], "contradictions": [], "interpretation_state": "enum"}}, ensure_ascii=False)

    def _parse(self, payload: Mapping[str, Any], request: str, request_id: str) -> CandidateInterpretation:
        def parse(items, polarity=Polarity.POSITIVE):
            result = []
            for item in items or []:
                if not isinstance(item, Mapping):
                    raise ValueError("constraint entries must be objects")
                result.append(CandidateConstraint(field=str(item["field"]), operator=str(item["operator"]), raw_value=item.get("raw_value", item.get("value")), normalized_value=item.get("normalized_value", item.get("value")), polarity=Polarity(str(item.get("polarity", polarity.value))), strength=str(item.get("strength", "hard")), support_state=SupportState(str(item.get("support_state", "supported"))), source_span=item.get("source_span"), rationale=item.get("rationale")))
            return tuple(result)
        state = InterpretationState(str(payload.get("interpretation_state", "NEEDS_CONFIRMATION")))
        return CandidateInterpretation(request_id=request_id, natural_language_request=request, semantic_query=str(payload.get("semantic_query", request)), constraints=parse(payload.get("constraints")), exclusions=parse(payload.get("exclusions"), Polarity.EXCLUSION), soft_preferences=parse(payload.get("soft_preferences")), unsupported_items=tuple(map(str, payload.get("unsupported_items", []))), unresolved_items=tuple(map(str, payload.get("unresolved_items", []))), contradictions=tuple(map(str, payload.get("contradictions", []))), interpretation_state=state, normalization={"arm": self.identity}, evidence=())


class HybridExtractor:
    identity = "hybrid-rule-plus-structured-qwen3-4b-v1"

    def __init__(self, *, model: str = "qwen3:4b", timeout_seconds: float = 90.0):
        self.rule = RuleExtractor()
        self.model = OllamaStructuredExtractor(model=model, timeout_seconds=timeout_seconds)

    def extract(self, natural_language_request: str, *, request_id: str) -> ExtractionResult:
        # Rules own explicit evidence. Model reconciliation is intentionally
        # deferred when no typed conflict resolver is available.
        result = self.model.extract(natural_language_request, request_id=request_id)
        if result.status == "NOT_RUN":
            return ExtractionResult(None, self.identity, "NOT_RUN", result.latency_ms, {"rule_arm": self.rule.identity, "model_arm": self.model.identity}, result.error)
        rule_result = self.rule.extract(natural_language_request, request_id=request_id)
        if rule_result.interpretation and result.interpretation:
            # Conservative reconciliation: preserve explicit rule evidence and
            # do not let a model override it. A typed conflict is visible.
            return ExtractionResult(rule_result.interpretation, self.identity, "COMPLETED", rule_result.latency_ms + result.latency_ms, {"rule_arm": self.rule.identity, "model_arm": self.model.identity, "reconciliation": "rules_authoritative_explicit_patterns"})
        return ExtractionResult(None, self.identity, "INVALID_OUTPUT", rule_result.latency_ms + result.latency_ms, {}, "rule/model reconciliation failed")


class RuleExtractorV3(RuleExtractor):
    """Conservative Gate 3D rules: mention/context never implies eligibility."""

    identity = "rule-conservative-v3-gate3d"

    def extract(self, natural_language_request: str, *, request_id: str) -> ExtractionResult:
        text = natural_language_request.strip()
        lower = text.lower()
        base = super().extract(text, request_id=request_id)
        if base.interpretation is None:
            return ExtractionResult(None, self.identity, base.status, base.latency_ms, base.metadata, base.error)
        # Keep numeric/operator handling from the v1 parser, but remove
        # categorical HARD assertions unless requirement language is explicit.
        explicit = re.compile(r"\b(?:must|required|required:\s*|only|at least|no less than)\b", re.I)
        constraints = []
        soft = list(base.interpretation.soft_preferences)
        for item in base.interpretation.constraints:
            if item.field == "years_experience":
                constraints.append(item)
            elif item.field == "industry":
                value = str(item.normalized_value).lower()
                before = lower[: max(0, lower.find(value))]
                if explicit.search(before) or re.search(rf"\bexperts?\s+(?:in|from)\s+{re.escape(value)}\b", lower) or re.search(rf"\b{re.escape(value)}\s+experts?\b", lower):
                    constraints.append(item)
            elif item.field == "role":
                if explicit.search(lower) or re.search(r"\b(?:principal|senior)-level\b", lower):
                    constraints.append(item)
            elif item.field == "seniority":
                if explicit.search(lower) or re.search(r"\bprincipal-level\b", lower):
                    constraints.append(item)
            elif item.field == "location":
                if explicit.search(lower):
                    constraints.append(item)
        exclusions = []
        # Re-scan exclusions independently: the same canonical value may occur
        # once as a required category and again in an exclusion clause.
        for value in CANONICAL_VALUES["industry"]:
            if re.search(rf"\b(?:excluding|exclude|must not|avoid)\b[^.]*\b{re.escape(value)}\b", lower):
                exclusions.append(_constraint("industry", "neq", value, polarity=Polarity.EXCLUSION, source=value))
        for item in base.interpretation.exclusions:
            value = str(item.normalized_value).lower()
            before = lower[: max(0, lower.find(value))]
            if re.search(r"\bnot necessarily\b|\bprefer(?:ably)?\b|\bideally\b", before):
                continue
            if re.search(rf"\b(?:excluding|exclude|must not|avoid)\b[^.]*\b{re.escape(value)}\b", lower) or re.search(r"\b(?:excluding|exclude|must not|avoid)\b", before):
                exclusions.append(item)
        # Recompute contradiction state over the normalized retained contract.
        contradictions = list(base.interpretation.contradictions)
        by_field: dict[str, list[CandidateConstraint]] = {}
        for item in tuple(constraints) + tuple(exclusions):
            by_field.setdefault(item.field, []).append(item)
        for field, items in by_field.items():
            positives = [i for i in items if i.polarity is Polarity.POSITIVE]
            negatives = [i for i in items if i.polarity is Polarity.EXCLUSION]
            if any(p.field == field and any(n.normalized_value == p.normalized_value for n in negatives) for p in positives):
                contradictions.append(f"{field} positive and exclusion constraints conflict")
            if field == "years_experience":
                lower_bounds = [int(i.normalized_value) for i in positives if i.operator in {"gte", "gt"} and str(i.normalized_value).isdigit()]
                upper_bounds = [int(i.normalized_value) for i in positives if i.operator in {"lt", "lte"} and str(i.normalized_value).isdigit()]
                if lower_bounds and upper_bounds and max(lower_bounds) >= min(upper_bounds):
                    contradictions.append(f"years_experience lower bound conflicts with upper bound")
        state = InterpretationState.CONTRADICTORY if contradictions else _state(constraints, exclusions, soft, base.interpretation.unsupported_items, base.interpretation.unresolved_items, ())
        interpretation = CandidateInterpretation(request_id=request_id, natural_language_request=text, semantic_query=base.interpretation.semantic_query, constraints=tuple(constraints), exclusions=tuple(exclusions), soft_preferences=tuple(soft), unsupported_items=base.interpretation.unsupported_items, unresolved_items=base.interpretation.unresolved_items, contradictions=tuple(dict.fromkeys(contradictions)), interpretation_state=state, normalization={"arm": self.identity}, evidence=base.interpretation.evidence)
        errors = interpretation.validate()
        return ExtractionResult(None, self.identity, "INVALID_OUTPUT", base.latency_ms, {"errors": errors}, "; ".join(errors)) if errors else ExtractionResult(interpretation, self.identity, "COMPLETED", base.latency_ms, {"rules_version": self.identity, "registry_id": REGISTRY_ID})


class OllamaStructuredExtractorV2(OllamaStructuredExtractor):
    """Gate 3D model arm with explicit conservative extraction guidance."""

    identity = "ollama-structured-qwen3-4b-v2-gate3d"
    prompt_fingerprint = "gate3d-structured-v2"

    def _prompt(self, request: str) -> str:
        return json.dumps({"task": "Extract a candidate interpretation only; never execute retrieval.", "request": request, "policy": ["A HARD constraint requires explicit requirement language (must, required, only, at least).", "A mention, descriptive role/title, or contextual industry is not a HARD constraint.", "Preserve every supported HARD constraint even when unsupported phrases coexist.", "Preserve unsupported and ambiguous phrases visibly; never invent registry values.", "Prefer abstention or NEEDS_CONFIRMATION over unsupported hardening."], "operators": {"at least": "gte", "more than": "gt", "exactly": "eq", "under": "lt", "between": "between", "around": "ambiguous"}, "registry_id": REGISTRY_ID, "supported_fields": ["industry", "role", "location", "years_experience", "seniority"], "output": {"semantic_query": "string", "constraints": [], "exclusions": [], "soft_preferences": [], "unsupported_items": [], "unresolved_items": [], "contradictions": [], "interpretation_state": "enum"}}, ensure_ascii=False)


class CascadeExtractorV2:
    """Rules-first cascade with deterministic, safety-first reconciliation."""

    identity = "cascade-conservative-v2-gate3d"
    routing_identity = "explicit-coverage-v1"
    reconciliation_identity = "safety-first-candidate-v1"
    prompt_fingerprint = "gate3d-structured-v2"

    def __init__(self, *, model: str = "qwen3:4b", timeout_seconds: float = 15.0):
        self.rule = RuleExtractorV3()
        self.model = OllamaStructuredExtractorV2(model=model, timeout_seconds=timeout_seconds)

    def _fully_resolved(self, result: ExtractionResult) -> bool:
        if result.interpretation is None:
            return False
        i = result.interpretation
        return not i.unsupported_items and not i.unresolved_items and not i.contradictions and i.interpretation_state is not InterpretationState.AMBIGUOUS

    def extract(self, natural_language_request: str, *, request_id: str) -> ExtractionResult:
        rule = self.rule.extract(natural_language_request, request_id=request_id)
        if self._fully_resolved(rule):
            return ExtractionResult(rule.interpretation, self.identity, "COMPLETED", rule.latency_ms, {"route": "rules_only", "routing_identity": self.routing_identity, "model_invoked": False, "reconciliation": self.reconciliation_identity})
        model = self.model.extract(natural_language_request, request_id=request_id)
        if model.status != "COMPLETED" or model.interpretation is None:
            return ExtractionResult(rule.interpretation if rule.interpretation else None, self.identity, rule.status if rule.interpretation else model.status, rule.latency_ms + model.latency_ms, {"route": "model", "routing_identity": self.routing_identity, "model_invoked": True, "reconciliation": self.reconciliation_identity}, model.error)
        # Deterministic safety-first reconciliation: explicit conservative rule
        # evidence is retained; model-only HARD proposals require confirmation.
        if rule.interpretation and rule.interpretation.constraints:
            chosen = rule.interpretation
        else:
            chosen = model.interpretation
            chosen = CandidateInterpretation(request_id=chosen.request_id, natural_language_request=chosen.natural_language_request, semantic_query=chosen.semantic_query, constraints=tuple(c if c.strength == "soft" else CandidateConstraint(c.field, c.operator, c.raw_value, c.normalized_value, c.polarity, "soft", c.support_state, c.ambiguity_state, c.source_span, c.rationale) for c in chosen.constraints), exclusions=chosen.exclusions, soft_preferences=chosen.soft_preferences, unsupported_items=chosen.unsupported_items, unresolved_items=chosen.unresolved_items, contradictions=chosen.contradictions, interpretation_state=InterpretationState.NEEDS_CONFIRMATION, normalization={"arm": self.identity}, evidence=chosen.evidence)
        return ExtractionResult(chosen, self.identity, "COMPLETED", rule.latency_ms + model.latency_ms, {"route": "model_reconciled", "routing_identity": self.routing_identity, "model_invoked": True, "reconciliation": self.reconciliation_identity})
