import unittest

from scripts.run_v050_gate6 import metrics


class Gate6MetricSemanticsTests(unittest.TestCase):
    def _metric(self, *, eligible, prohibited, has_exclusions=True, grades=None):
        return metrics(["a", "b"], grades or {"a": 3, "b": 0}, top5_ids=["a", "b"], eligible=set(eligible), hard=set(), supply=1, prohibited=set(prohibited), has_exclusions=has_exclusions)

    def test_required_violation_is_not_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited=set())["prohibited_constraint_violation_at_5"], 0.0)

    def test_explicit_exclusion_violation_is_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited={"b"})["prohibited_constraint_violation_at_5"], 0.5)

    def test_required_violation_with_exclusion_satisfied_is_not_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited=set())["prohibited_constraint_violation_at_5"], 0.0)

    def test_required_satisfied_with_exclusion_violated_is_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited={"a"})["prohibited_constraint_violation_at_5"], 0.5)

    def test_one_of_multiple_exclusions_is_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited={"b"})["prohibited_constraint_violation_at_5"], 0.5)

    def test_all_exclusions_satisfied_are_not_prohibited(self):
        self.assertEqual(self._metric(eligible={"a", "b"}, prohibited=set())["prohibited_constraint_violation_at_5"], 0.0)

    def test_no_exclusions_is_not_applicable(self):
        self.assertIsNone(self._metric(eligible={"a"}, prohibited={"b"}, has_exclusions=False)["prohibited_constraint_violation_at_5"])

    def test_unknown_required_is_not_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited=set())["prohibited_constraint_violation_at_5"], 0.0)

    def test_hard_negative_does_not_imply_prohibited(self):
        self.assertEqual(self._metric(eligible={"a"}, prohibited=set(), grades={"a": 2, "b": 0})["prohibited_constraint_violation_at_5"], 0.0)


if __name__ == "__main__":
    unittest.main()
