import unittest
from fastapi.testclient import TestClient

from services.api.app import app


class WorkbenchApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_capabilities(self):
        self.assertEqual(self.client.get("/api/v1/health").status_code, 200)
        self.assertIn("hybrid", self.client.get("/api/v1/capabilities").json()["retrieval_strategies"])

    def test_v040_dataset_and_benchmark_discovery(self):
        datasets = self.client.get("/api/v1/datasets")
        benchmarks = self.client.get("/api/v1/benchmarks")
        self.assertEqual(datasets.status_code, 200)
        self.assertEqual(benchmarks.status_code, 200)
        self.assertEqual(datasets.json()["datasets"][0]["dataset_id"], "expert-discovery")
        self.assertEqual(benchmarks.json()["benchmarks"][0]["query_count"], 120)

    def test_session_query_trace_and_followup(self):
        session = self.client.post("/api/v1/sessions").json()
        response = self.client.post("/api/v1/query", json={"query": "Find healthcare experts with Azure AI experience", "session_id": session["session_id"]})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["results"])
        self.assertEqual(payload["verification"]["status"], "passed")
        self.assertIn("findings", payload["verification"])
        self.assertIn("evidence_by_result", payload)
        self.assertIn("raw_trace", payload)
        self.assertTrue(any(stage["stage"] == "fusion" for stage in payload["stage_summaries"]))
        self.assertEqual(payload["metrics"]["quality_status"], "unlabelled")
        self.assertEqual(self.client.get(payload["trace_url"]).status_code, 200)
        follow = self.client.post("/api/v1/query", json={"query": "only those in Portugal", "session_id": session["session_id"]}).json()
        self.assertIn("follow-up", follow["query"]["resolved"])

    def test_query_lab(self):
        cases = self.client.get("/api/v1/query-lab/cases").json()["cases"]
        self.assertTrue(cases)
        run = self.client.post("/api/v1/query-lab/runs", json={"case_id": cases[0]["id"]}).json()
        self.assertTrue(run["run_id"])
        other = self.client.post("/api/v1/query-lab/runs", json={"case_id": cases[0]["id"], "profile": "baseline"}).json()
        compare = self.client.post("/api/v1/query-lab/compare", json={"left_run_id": run["run_id"], "right_run_id": other["run_id"]})
        self.assertEqual(compare.status_code, 200)
        self.assertIn("score_comparison", compare.json())

    def test_score_semantics_and_execution_context(self):
        baseline = self.client.post("/api/v1/query", json={"query": "Find healthcare experts with Azure AI experience", "profile": "baseline"}).json()
        model = self.client.post("/api/v1/query", json={"query": "Find healthcare experts with Azure AI experience", "profile": "model-enhanced"}).json()
        self.assertTrue(all(item["score_type"] == "RRF fused score" for item in baseline["results"]))
        self.assertTrue(all(item["score_type"] == "Cross-Encoder score" for item in model["results"]))
        self.assertEqual(model["execution_context"]["planner"]["actual_provider"], "ollama")
        self.assertEqual(model["execution_context"]["reranker"]["actual_provider"], "bge_cross_encoder")
        self.assertIn("reranker_raw", model["results"][0]["score_stack"])

    def test_typed_errors(self):
        response = self.client.post("/api/v1/query", json={"query": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())


if __name__ == "__main__":
    unittest.main()
