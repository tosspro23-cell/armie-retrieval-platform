"""Opt-in real Gate 4 execution test; never uses mocks or fallback backends."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(
    os.getenv("ARMIE_RUN_ELASTICSEARCH_INTEGRATION") == "1",
    "set ARMIE_RUN_ELASTICSEARCH_INTEGRATION=1 to run real Gate 4",
)
class RealGate4IntegrationTests(unittest.TestCase):
    def test_h1_to_h4_execute_through_shared_runtime(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        with tempfile.NamedTemporaryFile(suffix=".json") as output:
            completed = subprocess.run(
                [sys.executable, "examples/run_v040_gate4.py", "--index", os.getenv("ARMIE_ELASTICSEARCH_TEST_INDEX", "armie-experts-read"), "--output", output.name],
                cwd=repo,
                env={**os.environ, "PYTHONPATH": str(repo / "src")},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(Path(output.name).read_text(encoding="utf-8"))
        self.assertEqual([profile["profile_id"] for profile in payload["profiles"]], ["H1", "H2", "H3", "H4"])
        h3 = payload["profiles"][2]["rows"][0]
        h4 = payload["profiles"][3]["rows"][0]
        self.assertTrue(h3["fusion"])
        self.assertEqual(h3["reranking"]["candidate_count_in"], 30)
        self.assertEqual(h4["reranking"]["actual_provider"], "bge_cross_encoder")
        self.assertTrue(any(row["reranking"]["model_load_latency_ms"] > 0 for row in payload["profiles"][3]["rows"]))
        self.assertTrue(any(row["reranking"]["model_load_latency_ms"] == 0 for row in payload["profiles"][3]["rows"][1:]))


if __name__ == "__main__":
    unittest.main()
