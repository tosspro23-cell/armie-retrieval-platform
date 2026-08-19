import unittest

from armie_retrieval.interpretation import InterpretationState, RuleExtractor


class Gate2ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = RuleExtractor()

    def test_common_rule_output_is_candidate_only(self):
        result = self.extractor.extract("Find Healthcare experts with at least 20 years.", request_id="q1")
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.interpretation.interpretation_state, InterpretationState.NEEDS_CONFIRMATION)
        self.assertEqual({item.field for item in result.interpretation.constraints}, {"industry", "years_experience"})
        self.assertFalse(hasattr(result.interpretation, "compile"))

    def test_preference_does_not_become_hard(self):
        result = self.extractor.extract("Prefer senior candidates, ideally Healthcare.", request_id="q2")
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.interpretation.constraints, ())
        self.assertTrue(result.interpretation.soft_preferences)

    def test_unsupported_and_contradiction_remain_visible(self):
        unsupported = self.extractor.extract("Find Healthcare experts who delivered projects for Microsoft in the last 3 years.", request_id="q3")
        self.assertTrue(unsupported.interpretation.unsupported_items)
        contradiction = self.extractor.extract("Find experts with at least 20 years and under 10 years.", request_id="q4")
        self.assertEqual(contradiction.interpretation.interpretation_state, InterpretationState.CONTRADICTORY)
        self.assertTrue(contradiction.interpretation.contradictions)

    def test_semantic_only_does_not_invent_hard_constraint(self):
        result = self.extractor.extract("Find experts experienced with Azure AI architecture.", request_id="q5")
        self.assertEqual(result.interpretation.interpretation_state, InterpretationState.NO_HARD_CONSTRAINTS)
        self.assertEqual(result.interpretation.constraints, ())


if __name__ == "__main__":
    unittest.main()
