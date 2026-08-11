import unittest
from fastapi.testclient import TestClient

from services.api.app import app


class WorkbenchApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_capabilities(self):
        health = self.client.get("/api/v1/health")
        capabilities = self.client.get("/api/v1/capabilities")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["package_version"], "0.4.0")
        self.assertTrue(health.json()["package_source"].endswith("/src/armie_retrieval"))
        self.assertEqual(health.json()["frontend_version"], "0.4.0")
        self.assertIn("hybrid", capabilities.json()["retrieval_strategies"])
        self.assertEqual(capabilities.json()["application_version"], "0.4.0")

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

    def test_free_query_defaults_to_v040_dataset_v2_dense_profile(self):
        payload = self.client.post("/api/v1/query", json={"query": "Find healthcare experts with Azure AI experience"}).json()
        self.assertEqual(payload["profile"], "H2")
        self.assertEqual(payload["dataset_context"]["dataset"], "Expert Discovery v2")
        self.assertEqual(payload["dataset_context"]["quality_status"], "unlabelled")
        self.assertTrue(all(item["id"].startswith("expert-v2-") for item in payload["results"]))
        self.assertTrue(all(item["score_type"] == "Dense score" for item in payload["results"]))

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

    def test_benchmark_profile_score_semantics(self):
        for profile, expected in (("H1", "BM25 score"), ("H2", "Dense score"), ("H3", "RRF fused score"), ("H4", "BGE Cross-Encoder score")):
            payload = self.client.post("/api/v1/benchmark/execute", json={"query_id": "v2-q-001", "profile": profile}).json()
            self.assertTrue(payload["results"])
            self.assertTrue(all(item["score_type"] == expected for item in payload["results"]))
        h2 = self.client.post("/api/v1/benchmark/execute", json={"query_id": "v2-q-001", "profile": "H2"}).json()
        self.assertTrue(all("reranker" not in item["score_type"].lower() for item in h2["results"]))
        self.assertTrue(all("Dense" in item["score_source"] for item in h2["results"]))

    def test_typed_errors(self):
        response = self.client.post("/api/v1/query", json={"query": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_gate6_benchmark_library_manifest_and_real_labelled_execution(self):
        profiles = self.client.get("/api/v1/benchmark/profiles").json()["profiles"]
        self.assertEqual([item["id"] for item in profiles], ["H1", "H2", "H3", "H4"])
        queries = self.client.get("/api/v1/benchmark/queries").json()["queries"]
        self.assertEqual(len(queries), 120)
        self.assertIn(queries[0]["label_status"], {"Gold", "Silver"})
        self.assertIn("canonical_required", queries[0])
        manifest = self.client.get("/api/v1/benchmark/manifest").json()
        self.assertTrue(manifest["available"])
        self.assertEqual(manifest["embedding_dimensions"], 1024)
        run = self.client.post("/api/v1/benchmark/execute", json={"query_id": "v2-q-001", "profile": "H2"})
        self.assertEqual(run.status_code, 200)
        payload = run.json()
        self.assertEqual(payload["profile"], "H2")
        self.assertEqual(payload["benchmark"]["label_status"], "Gold")
        self.assertIn("recall_denominator", payload["metrics"])
        self.assertTrue(any(item.get("judgement_grade") is not None for item in payload["results"]))


if __name__ == "__main__":
    unittest.main()
