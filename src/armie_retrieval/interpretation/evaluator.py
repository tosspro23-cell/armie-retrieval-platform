"""Deterministic Gate 1 interpretation evaluator.

The evaluator compares candidate interpretations with trusted gold objects. It
does not call models, infer meaning, compile contracts, or rank documents.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import CandidateConstraint, CandidateInterpretation, InterpretationState


@dataclass(frozen=True)
class EvaluationResult:
    exact_candidate_contract_match: bool
    constraint_true_positives: int
    constraint_false_positives: int
    constraint_missed_hard: int
    constraint_precision: float
    constraint_recall: float
    false_hard_constraint_count: int
    false_exclusion_count: int
    false_hard_query: bool
    missed_hard_query: bool
    unsupported_items_correct: bool
    ambiguity_state_correct: bool
    contradiction_state_correct: bool
    semantic_intent_evaluated_separately: bool = True

    @property
    def false_hard_rate_denominator_unit(self) -> str:
        return "query" if self.false_hard_query else "none"


def _hard_constraints(item: CandidateInterpretation) -> set[tuple]:
    return {
        c.key()
        for c in item.constraints + item.exclusions
        if c.strength == "hard" and c.support_state.value == "supported"
    }


def _all_contract_constraints(item: CandidateInterpretation) -> set[tuple]:
    return {c.key() for c in item.constraints + item.exclusions if c.strength == "hard"}


def evaluate_interpretation(gold: CandidateInterpretation, predicted: CandidateInterpretation) -> EvaluationResult:
    """Compare one prediction with gold using explicit slot-level semantics."""
    gold_hard = _hard_constraints(gold)
    predicted_hard = _all_contract_constraints(predicted)
    tp = len(gold_hard & predicted_hard)
    fp = len(predicted_hard - gold_hard)
    missed = len(gold_hard - predicted_hard)
    precision = tp / len(predicted_hard) if predicted_hard else (1.0 if not gold_hard else 0.0)
    recall = tp / len(gold_hard) if gold_hard else (1.0 if not predicted_hard else 0.0)
    exact = (
        gold_hard == predicted_hard
        and tuple(gold.unsupported_items) == tuple(predicted.unsupported_items)
        and tuple(gold.unresolved_items) == tuple(predicted.unresolved_items)
        and tuple(gold.contradictions) == tuple(predicted.contradictions)
        and gold.interpretation_state is predicted.interpretation_state
    )
    return EvaluationResult(
        exact_candidate_contract_match=exact,
        constraint_true_positives=tp,
        constraint_false_positives=fp,
        constraint_missed_hard=missed,
        constraint_precision=precision,
        constraint_recall=recall,
        false_hard_constraint_count=fp,
        false_exclusion_count=sum(1 for key in (predicted_hard - gold_hard) if key[3] == "exclusion"),
        false_hard_query=fp > 0,
        missed_hard_query=missed > 0,
        unsupported_items_correct=tuple(gold.unsupported_items) == tuple(predicted.unsupported_items),
        ambiguity_state_correct=(gold.interpretation_state is InterpretationState.AMBIGUOUS) == (predicted.interpretation_state is InterpretationState.AMBIGUOUS),
        contradiction_state_correct=(gold.interpretation_state is InterpretationState.CONTRADICTORY) == (predicted.interpretation_state is InterpretationState.CONTRADICTORY),
    )
