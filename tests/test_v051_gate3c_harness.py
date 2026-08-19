import tempfile
import unittest
from pathlib import Path

from armie_retrieval.interpretation.extractors import ExtractionResult
from scripts.run_v051_gate3c_resumable import run_resumable
from scripts.run_v051_gate3_evaluation import build_gold

_RECORDS = {f"q{i}": {"query_id": f"q{i}", "stratum": "exact", "natural_language_request": f"query {i}", "semantic_intent": f"intent {i}", "expected_constraints": [], "expected_exclusions": [], "soft_preferences": [], "unsupported_items": [], "ambiguity": [], "contradictions": [], "state": "NO_HARD_CONSTRAINTS"} for i in range(3)}

class _FakeArm:
    def __init__(self, identity="fake-gate3c-v1"): self.identity, self.calls = identity, []
    def extract(self, text, *, request_id):
        self.calls.append(request_id); return ExtractionResult(build_gold(_RECORDS[request_id]), self.identity, "COMPLETED", 1.0, {"fake": True})

class Gate3CResumableHarnessTests(unittest.TestCase):
    def test_durable_checkpoint_and_resume_without_duplicate_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "run.jsonl"; arm = _FakeArm()
            with self.assertRaises(KeyboardInterrupt): run_resumable(list(_RECORDS.values()), arm, checkpoint, timeout=15, interrupt_after=2)
            self.assertEqual(len(checkpoint.read_text().splitlines()), 2)
            resumed = run_resumable(list(_RECORDS.values()), arm, checkpoint, timeout=15)
            self.assertEqual(resumed["status"], "COMPLETED"); self.assertEqual(resumed["integrity"]["missing_ids"], []); self.assertEqual(arm.calls, ["q0", "q1", "q2"])

    def test_identity_mismatch_refuses_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "run.jsonl"; records = list(_RECORDS.values())
            run_resumable(records, _FakeArm("one"), checkpoint, timeout=15)
            with self.assertRaisesRegex(ValueError, "identity mismatch"): run_resumable(records, _FakeArm("two"), checkpoint, timeout=15)
