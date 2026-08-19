import unittest

from armie_retrieval.interpretation import (
    ModelAssistedStagedExtractor,
    SemanticRole,
    StageGold,
    role_metrics,
    staged_extract,
)


class Gate3FStagedTests(unittest.TestCase):
    def test_context_only_never_becomes_hard(self):
        result = staged_extract("worked on Healthcare products")
        self.assertFalse(result.interpretation.constraints)
        self.assertEqual(result.roles[0].role, SemanticRole.CONTEXT_ONLY)

    def test_explicit_requirement_and_exclusion(self):
        result = staged_extract("Healthcare experts only and excluding energy")
        self.assertEqual([c.field for c in result.interpretation.constraints], ["industry"])
        self.assertEqual([c.field for c in result.interpretation.exclusions], ["industry"])
        self.assertEqual(result.interpretation.constraints[0].raw_value, "healthcare")
        self.assertEqual(result.interpretation.exclusions[0].raw_value, "energy")

    def test_preference_does_not_harden(self):
        result = staged_extract("preferably based in London")
        self.assertFalse(result.interpretation.constraints)
        self.assertTrue(result.interpretation.soft_preferences)

    def test_numeric_normalization_is_deterministic(self):
        result = staged_extract("at least 20 years")
        constraint = result.interpretation.constraints[0]
        self.assertEqual((constraint.field, constraint.operator, constraint.normalized_value), ("years_experience", "gte", 20))

    def test_ambiguous_numeric_does_not_harden(self):
        result = staged_extract("around 20 years")
        self.assertFalse(result.interpretation.constraints)
        self.assertEqual(result.roles[0].role, SemanticRole.AMBIGUOUS)

    def test_stage_metrics_and_provenance(self):
        result = staged_extract("must be based in London", request_id="g3f-test")
        self.assertEqual(result.schema_version, "staged-interpretation-v1")
        self.assertIn("required_count", result.metrics)
        self.assertTrue(all("role" in evidence for evidence in result.interpretation.evidence))

    def test_role_metric_false_required(self):
        gold = [StageGold("q1", {"worked on Healthcare products": SemanticRole.CONTEXT_ONLY})]
        prediction = {"q1": staged_extract("worked on Healthcare products", request_id="q1")}
        metrics = role_metrics(gold, prediction)
        self.assertEqual(metrics["false_required_rate"], 0.0)
        self.assertEqual(metrics["context_only_accuracy"], 1.0)

    def test_model_arm_is_bounded_and_falls_back_without_ollama(self):
        result = ModelAssistedStagedExtractor(timeout_seconds=0.01).extract("at least 20 years")
        self.assertIn(result.metrics.get("fallback"), (None, "deterministic-staged-v1"))
        self.assertEqual(result.interpretation.constraints[0].field, "years_experience")


if __name__ == "__main__":
    unittest.main()
