import tempfile
import unittest
from pathlib import Path

from armie_retrieval.application.workbench import WorkbenchError, WorkbenchService
from fastapi.testclient import TestClient
from services.api.app import app


class Gate4WorkbenchProtocolTests(unittest.TestCase):
    def setUp(self):
        self.service = WorkbenchService(Path(tempfile.mkdtemp()))

    def test_unambiguous_query_requires_confirmation_then_validates(self):
        state = self.service.interpret("Find principal search engineers")
        self.assertEqual(state["state"], "INTERPRETATION_COMPLETE")
        self.assertTrue(state["confirmation_required"])
        validated = self.service.confirm_interpretation(state["session_id"])
        self.assertEqual(validated["state"], "VALIDATED_CONTRACT")

    def test_ambiguous_query_blocks_until_resolution_and_confirm(self):
        state = self.service.interpret("Find experts with around 20 years experience")
        self.assertEqual(state["state"], "NEEDS_CLARIFICATION")
        item = state["clarifications"][0]
        self.assertIn("MINIMUM", item["allowed_resolutions"])
        resolved = self.service.resolve_interpretation(state["session_id"], {
            "clarification_id": item["clarification_id"],
            "selected_resolution": "MINIMUM",
            "source": "workbench",
        })
        self.assertEqual(resolved["state"], "INTERPRETATION_COMPLETE")
        self.assertEqual(self.service.confirm_interpretation(state["session_id"])["state"], "VALIDATED_CONTRACT")

    def test_unknown_or_disallowed_resolution_is_rejected(self):
        state = self.service.interpret("Find maybe healthcare experts")
        item = state["clarifications"][0]
        with self.assertRaises(WorkbenchError):
            self.service.resolve_interpretation(state["session_id"], {
                "clarification_id": item["clarification_id"],
                "selected_resolution": "NOT_A_REAL_CHOICE",
            })
        with self.assertRaises(WorkbenchError):
            self.service.resolve_interpretation(state["session_id"], {
                "clarification_id": "missing",
                "selected_resolution": "REQUIRED",
            })

    def test_clarification_resolution_does_not_execute_retrieval(self):
        state = self.service.interpret("Find experts with around 20 years")
        item = state["clarifications"][0]
        self.service.resolve_interpretation(state["session_id"], {
            "clarification_id": item["clarification_id"],
            "selected_resolution": "MINIMUM",
        })
        self.assertEqual(self.service.runs, {})

    def test_typed_api_endpoints_expose_protocol_states(self):
        client = TestClient(app)
        created = client.post("/api/v1/interpret", json={"query": "Find experts with around 20 years"})
        self.assertEqual(created.status_code, 200)
        payload = created.json()
        self.assertEqual(payload["state"], "NEEDS_CLARIFICATION")
        item = payload["clarifications"][0]
        resolved = client.post(f"/api/v1/interpretations/{payload['session_id']}/resolutions", json={
            "clarification_id": item["clarification_id"], "selected_resolution": "MINIMUM"
        })
        self.assertEqual(resolved.status_code, 200)
        confirmed = client.post(f"/api/v1/interpretations/{payload['session_id']}/confirm")
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(confirmed.json()["state"], "VALIDATED_CONTRACT")

    def test_execution_is_rejected_before_confirmation(self):
        state = self.service.interpret("Find experts with at least 20 years")
        with self.assertRaises(WorkbenchError) as caught:
            self.service.execute_interpretation(state["session_id"])
        self.assertEqual(caught.exception.code, "interpretation_not_confirmed")

    def test_legacy_query_cannot_bypass_unresolved_interpretation(self):
        state = self.service.interpret("Find healthcare experts with around 20 years")
        self.assertEqual(state["blocking_clarification_count"], 1)
        with self.assertRaises(WorkbenchError) as caught:
            self.service.query(state["interpretation"]["semantic_query"], session_id=state["session_id"], profile="H2")
        self.assertEqual(caught.exception.code, "interpretation_not_confirmed")

    def test_governed_fresh_query_auto_interprets_without_execution(self):
        result = self.service.query(
            "Find healthcare experts with Azure AI experience around 20 years",
            profile="H2",
            governed=True,
        )
        self.assertEqual(result["execution_status"], "blocked")
        self.assertEqual(result["state"], "NEEDS_CLARIFICATION")
        self.assertTrue(result["governed_mode"])
        self.assertEqual(self.service.runs, {})

    def test_governed_fresh_unambiguous_query_requires_confirmation(self):
        result = self.service.query(
            "Find principal search engineers",
            profile="H2",
            governed=True,
        )
        self.assertEqual(result["execution_status"], "blocked")
        self.assertEqual(result["state"], "INTERPRETATION_COMPLETE")
        self.assertTrue(result["confirmation_required"])
        self.assertEqual(self.service.runs, {})

    def test_governed_confirmed_session_executes_canonical_c1(self):
        state = self.service.query(
            "Find healthcare experts with at least 20 years",
            profile="H2",
            governed=True,
        )
        confirmed = self.service.confirm_interpretation(state["session_id"])
        self.service.structured_query = lambda text, payload, requested_k=5: {
            "profile": "C1", "results": [], "query": {"structured_contract": payload}
        }
        result = self.service.query(
            state["interpretation"]["semantic_query"],
            session_id=state["session_id"],
            profile="H2",
            governed=True,
        )
        self.assertEqual(result["profile"], "C1")
        self.assertEqual(result["query"]["structured_contract"], confirmed["contract"])

    def test_confirmed_execution_result_count_matches_items(self):
        state = self.service.interpret("Find experts with at least 20 years")
        confirmed = self.service.confirm_interpretation(state["session_id"])
        items = [{"id": f"expert-{i}", "rank": i + 1} for i in range(5)]
        self.service.structured_query = lambda text, payload, requested_k=5: {
            "profile": "C1", "results": items, "evidence": [{"evidence_id": "ev-1"}],
            "answer_summary": {"text": "5 results", "contract_state": "VALID"},
            "metrics": {"total_latency_ms": 1}, "execution_context": {},
            "stage_summaries": [], "verification": {"status": "passed", "findings": []},
            "query": {"structured_contract": payload},
        }
        result = self.service.execute_interpretation(state["session_id"], contract_fingerprint=confirmed["contract_fingerprint"])
        self.assertEqual(len(result["results"]), 5)
        self.assertEqual(result["answer_summary"]["contract_state"], "VALID")

    def test_confirmed_zero_result_is_distinct_from_no_execution(self):
        state = self.service.interpret("Find experts with at least 20 years")
        confirmed = self.service.confirm_interpretation(state["session_id"])
        self.service.structured_query = lambda text, payload, requested_k=5: {
            "profile": "C1", "results": [], "evidence": [],
            "answer_summary": {"text": "0 results", "contract_state": "VALID", "shortfall": {"count": 5}},
            "metrics": {"total_latency_ms": 1}, "execution_context": {},
            "stage_summaries": [], "verification": {"status": "passed", "findings": []},
            "query": {"structured_contract": payload},
        }
        result = self.service.execute_interpretation(state["session_id"], contract_fingerprint=confirmed["contract_fingerprint"])
        self.assertEqual(result["results"], [])
        self.assertEqual(result["answer_summary"]["text"], "0 results")
        self.assertNotEqual(result["answer_summary"]["text"], "Run a query to see the deterministic evidence summary.")

    def test_legacy_query_uses_canonical_c1_after_confirmation(self):
        state = self.service.interpret("Find healthcare experts with at least 20 years")
        confirmed = self.service.confirm_interpretation(state["session_id"])
        self.service.structured_query = lambda text, payload, requested_k=5: {"profile": "C1", "results": [], "query": {"structured_contract": payload}}
        result = self.service.query(state["interpretation"]["semantic_query"], session_id=state["session_id"], profile="H2")
        self.assertEqual(result["profile"], "C1")
        self.assertEqual(result["query"]["structured_contract"], confirmed["contract"])

    def test_confirmed_contract_executes_only_with_current_fingerprint(self):
        state = self.service.interpret("Find healthcare experts with at least 20 years")
        confirmed = self.service.confirm_interpretation(state["session_id"])
        self.assertEqual(confirmed["state"], "VALIDATED_CONTRACT")
        self.service.structured_query = lambda text, payload, requested_k=5: {"profile": "C1", "results": [], "query": {"structured_contract": payload}}
        result = self.service.execute_interpretation(state["session_id"], contract_fingerprint=confirmed["contract_fingerprint"])
        self.assertEqual(result["profile"], "C1")
        with self.assertRaises(WorkbenchError) as caught:
            self.service.execute_interpretation(state["session_id"], contract_fingerprint="stale")
        self.assertEqual(caught.exception.code, "stale_contract")

    def test_edit_after_confirmation_invalidates_execution(self):
        state = self.service.interpret("Find experts with around 20 years")
        item = state["clarifications"][0]
        resolved = self.service.resolve_interpretation(state["session_id"], {"clarification_id": item["clarification_id"], "selected_resolution": "MINIMUM"})
        confirmed = self.service.confirm_interpretation(state["session_id"])
        self.assertEqual(confirmed["state"], "VALIDATED_CONTRACT")
        edited = self.service.resolve_interpretation(state["session_id"], {"clarification_id": item["clarification_id"], "selected_resolution": "MAXIMUM"}, edit=True)
        self.assertEqual(edited["state"], "INTERPRETATION_COMPLETE")
        with self.assertRaises(WorkbenchError):
            self.service.execute_interpretation(state["session_id"])

    def test_unsupported_relationship_cannot_be_compiled(self):
        state = self.service.interpret("Find experts who worked at Acme")
        with self.assertRaises(WorkbenchError) as caught:
            self.service.confirm_interpretation(state["session_id"])
        self.assertEqual(caught.exception.code, "unsupported_executable_intent")

    def test_explicit_exclusion_converges_on_canonical_contract(self):
        state = self.service.interpret("Find healthcare experts excluding financial services")
        confirmed = self.service.confirm_interpretation(state["session_id"])
        self.assertEqual(confirmed["state"], "VALIDATED_CONTRACT")
        self.assertEqual(confirmed["contract"]["exclusions"][0]["canonical_field"], "industry")
        self.assertEqual(confirmed["contract"]["exclusions"][0]["operator"], "not_in")


if __name__ == "__main__":
    unittest.main()
