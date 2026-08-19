import json
import unittest
from pathlib import Path

from armie_retrieval.interpretation.serialization import fingerprint_records


class Gate3EvaluationTests(unittest.TestCase):
    root = Path(__file__).parents[1]

    def test_frozen_manifest_matches_fixture(self):
        manifest = json.loads((self.root / "docs/v0.5.1/gate3-evaluation-manifest.json").read_text())
        records = [json.loads(line) for line in (self.root / manifest["fixture"]).read_text().splitlines() if line.strip()]
        self.assertEqual(len(records), 120)
        self.assertEqual(fingerprint_records(records), manifest["fingerprint"])
        self.assertEqual(len({row["stratum"] for row in records}), 20)

    def test_thresholds_are_preregistered_and_safe(self):
        manifest = json.loads((self.root / "docs/v0.5.1/gate3-evaluation-manifest.json").read_text())
        thresholds = manifest["promotion_criteria_frozen_before_runs"]
        self.assertEqual(thresholds["false_hard_query_rate_max"], 0.0)
        self.assertEqual(thresholds["false_hard_constraint_rate_max"], 0.0)
        self.assertTrue(manifest["mandatory_confirmation"])
        self.assertFalse(manifest["c1_called"])

    def test_result_artifact_preserves_full_denominators_and_failure_classes(self):
        report = json.loads((self.root / "docs/v0.5.1/gate3-evaluation-results.json").read_text())
        self.assertEqual(report["item_count"], 120)
        for arm in report["arms"]:
            self.assertIn("attempted", arm["metrics"])
            self.assertIn("coverage", arm["metrics"])
            self.assertIn("failure_classes", arm["metrics"])
        self.assertFalse(report["c1_called"])


if __name__ == "__main__":
    unittest.main()
