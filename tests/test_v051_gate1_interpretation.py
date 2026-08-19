import json
import unittest
from pathlib import Path

from armie_retrieval.interpretation import (
    CandidateConstraint,
    CandidateInterpretation,
    InterpretationState,
    Polarity,
    SupportState,
    evaluate_interpretation,
    fingerprint_records,
)


def constraint(field, operator, value, *, strength="hard", polarity=Polarity.POSITIVE, support=SupportState.SUPPORTED):
    return CandidateConstraint(
        field=field,
        operator=operator,
        raw_value=value,
        normalized_value=value,
        strength=strength,
        polarity=polarity,
        support_state=support,
    )


def interpretation(request_id, state, constraints=(), exclusions=(), soft=(), unsupported=(), contradictions=()):
    return CandidateInterpretation(
        request_id=request_id,
        natural_language_request=request_id,
        semantic_query="semantic intent",
        constraints=tuple(constraints),
        exclusions=tuple(exclusions),
        soft_preferences=tuple(soft),
        unsupported_items=tuple(unsupported),
        contradictions=tuple(contradictions),
        interpretation_state=state,
    )


class Gate1InterpretationTests(unittest.TestCase):
    def test_schema_is_non_executable_and_validates_registry(self):
        item = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("industry", "eq", "healthcare")])
        self.assertEqual(item.schema_version, "nl-constraint-interpretation-v1")
        self.assertEqual(item.validate(), [])
        self.assertFalse(hasattr(item, "compile"))

    def test_exact_match_is_hand_computable(self):
        gold = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("years_experience", "gte", 20)])
        self.assertTrue(evaluate_interpretation(gold, gold).exact_candidate_contract_match)

    def test_added_false_hard_is_detected(self):
        gold = interpretation("q1", InterpretationState.NO_HARD_CONSTRAINTS)
        predicted = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("seniority", "gte", "senior")])
        result = evaluate_interpretation(gold, predicted)
        self.assertEqual(result.false_hard_constraint_count, 1)
        self.assertTrue(result.false_hard_query)

    def test_missed_hard_is_separate(self):
        gold = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("years_experience", "gte", 20)])
        predicted = interpretation("q1", InterpretationState.NO_HARD_CONSTRAINTS)
        result = evaluate_interpretation(gold, predicted)
        self.assertEqual(result.constraint_missed_hard, 1)
        self.assertFalse(result.false_hard_query)

    def test_wrong_operator_and_value_are_not_equivalent(self):
        gold = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("years_experience", "gte", 20)])
        predicted = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("years_experience", "gt", 20)])
        result = evaluate_interpretation(gold, predicted)
        self.assertFalse(result.exact_candidate_contract_match)
        self.assertEqual(result.constraint_true_positives, 0)

    def test_exclusion_polarity_is_part_of_matching(self):
        gold = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("industry", "eq", "healthcare")], [constraint("industry", "neq", "financial services", polarity=Polarity.EXCLUSION)])
        predicted = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("industry", "eq", "healthcare")], [constraint("industry", "eq", "financial services", polarity=Polarity.POSITIVE)])
        result = evaluate_interpretation(gold, predicted)
        self.assertEqual(result.constraint_true_positives, 1)
        self.assertEqual(result.constraint_false_positives, 1)

    def test_preference_hardened_is_false_hard(self):
        gold = interpretation("q1", InterpretationState.NO_HARD_CONSTRAINTS, soft=[constraint("seniority", "gte", "senior", strength="soft")])
        predicted = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("seniority", "gte", "senior")])
        self.assertTrue(evaluate_interpretation(gold, predicted).false_hard_query)

    def test_unsupported_omission_and_states_are_visible(self):
        gold = interpretation("q1", InterpretationState.PARTIALLY_SUPPORTED, [constraint("industry", "eq", "healthcare")], unsupported=["last 3 years"])
        predicted = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, [constraint("industry", "eq", "healthcare")])
        result = evaluate_interpretation(gold, predicted)
        self.assertFalse(result.unsupported_items_correct)
        self.assertFalse(result.exact_candidate_contract_match)

    def test_contradiction_must_be_typed(self):
        item = interpretation("q1", InterpretationState.CONTRADICTORY, [constraint("years_experience", "gte", 20), constraint("years_experience", "lt", 10)], contradictions=["conflicting bounds"])
        self.assertEqual(item.validate(), [])
        invalid = interpretation("q1", InterpretationState.NEEDS_CONFIRMATION, contradictions=["conflicting bounds"])
        self.assertTrue(any("CONTRADICTORY" in error for error in invalid.validate()))

    def test_gold_fixture_and_fingerprint_are_deterministic(self):
        path = Path(__file__).parent / "fixtures" / "v051_gate1_gold.jsonl"
        records = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(len(records), 20)
        self.assertEqual(fingerprint_records(records), fingerprint_records(records))
        self.assertEqual([record["state"] for record in records].count("NO_HARD_CONSTRAINTS"), 3)


if __name__ == "__main__":
    unittest.main()
