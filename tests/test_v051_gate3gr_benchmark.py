import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests/fixtures/v051_gate3gr_promotion_v2.json"


class Gate3GRBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE.read_text())

    def test_identity_and_deterministic_generation(self):
        first = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        subprocess.run([sys.executable, "scripts/build_v051_gate3gr_benchmark.py"], cwd=ROOT, check=True, capture_output=True, text=True)
        second = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        self.assertEqual(first, second)
        self.assertEqual(self.payload["benchmark_id"], "v0.5.1-staged-interpretation-promotion-v2")

    def test_no_exact_duplicates_and_mixed_coverage(self):
        normalized = [" ".join(item["request"].lower().split()) for item in self.payload["items"]]
        self.assertEqual(len(normalized), len(set(normalized)))
        self.assertGreaterEqual(sum(len(item["spans"]) > 1 for item in self.payload["items"]), 10)

    def test_role_strata_and_pattern_diversity(self):
        strata = {item.get("stratum", item["spans"][0]["role"]) for item in self.payload["items"]}
        self.assertTrue({"REQUIRED", "EXCLUDED", "PREFERRED", "CONTEXT_ONLY", "UNSUPPORTED", "AMBIGUOUS"} <= strata)
        families = {item["pattern_family"] for item in self.payload["items"]}
        self.assertGreaterEqual(len(families), 20)

    def test_structured_spans_have_required_truth(self):
        for item in self.payload["items"]:
            for span in item["spans"]:
                if span["role"] in {"REQUIRED", "EXCLUDED"}:
                    self.assertIn("field", span)
                    self.assertIn("operator", span)
                    self.assertIn("value", span)


if __name__ == "__main__":
    unittest.main()
