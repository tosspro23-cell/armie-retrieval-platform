import unittest

from armie_retrieval.interpretation import CascadeExtractorV2, InterpretationState, RuleExtractorV3


class Gate3DSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.rule = RuleExtractorV3()

    def test_context_is_not_requirement(self):
        result = self.rule.extract("Find experts with Healthcare experience.", request_id="q")
        self.assertEqual(result.interpretation.constraints, ())

    def test_explicit_requirement_is_hard(self):
        result = self.rule.extract("Find experts who must be in Healthcare.", request_id="q")
        self.assertEqual([(c.field, c.normalized_value) for c in result.interpretation.constraints], [("industry", "healthcare")])

    def test_numeric_truth_table(self):
        cases = {"at least 20": "gte", "more than 20": "gt", "exactly 20": "eq", "under 20": "lt", "between 10 and 20": "between"}
        for phrase, operator in cases.items():
            result = self.rule.extract(f"Find experts with {phrase} years.", request_id=phrase)
            self.assertEqual(result.interpretation.constraints[0].operator, operator)
        around = self.rule.extract("Find experts with around 20 years.", request_id="around")
        self.assertEqual(around.interpretation.constraints, ())
        self.assertEqual(around.interpretation.interpretation_state, InterpretationState.AMBIGUOUS)

    def test_exclusion_and_contradiction_scope(self):
        result = self.rule.extract("Find Healthcare experts excluding Healthcare.", request_id="q")
        self.assertEqual(result.interpretation.interpretation_state, InterpretationState.CONTRADICTORY)
        preference = self.rule.extract("Prefer candidates outside Healthcare.", request_id="p")
        self.assertEqual(preference.interpretation.exclusions, ())

    def test_cascade_has_selective_rules_only_route(self):
        cascade = CascadeExtractorV2(timeout_seconds=0.01)
        result = cascade.extract("Find experts with at least 20 years.", request_id="q")
        self.assertEqual(result.metadata["route"], "rules_only")
        self.assertFalse(result.metadata["model_invoked"])
