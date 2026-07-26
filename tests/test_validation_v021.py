from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.benchmarking import generate_benchmark_dataset, load_experts
from armie_retrieval.embeddings import create_embedding_provider
from armie_retrieval.evaluation import evaluate, run_evaluation
from armie_retrieval.indexing import GraphIndexBuilder, KeywordIndexBuilder, VectorIndexBuilder
from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult, ResultItem
from armie_retrieval.planners import OllamaStructuredLLMClient, RuleBasedPlanner
from armie_retrieval.production import ProductionArtifacts, create_production_platform


class FixedEmbeddingProvider:
    dimension = 4

    def embed(self, texts):
        return [[float(len(text) % 5), 1.0, 2.0, 3.0] for text in texts]


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeSession:
    def get(self, url, timeout):
        return FakeResponse({"models": [{"name": "local-model"}]})

    def post(self, url, json, timeout):
        return FakeResponse({"response": '{"strategy": "dense", "processors": [], "top_k": 2}'})


class ValidationV021Test(unittest.TestCase):
    def test_embedding_provider_is_configuration_selected(self) -> None:
        provider = create_embedding_provider({"embedding": {"provider": "bge", "model": "local-bge"}})
        self.assertEqual(provider.model_name, "local-bge")

    def test_persistent_artifacts_support_production_retrievers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            dataset = generate_benchmark_dataset(root, size=50)
            artifacts = ProductionArtifacts(root / "indexes")
            embedding = FixedEmbeddingProvider()
            VectorIndexBuilder(embedding).build(dataset.experts, artifacts.vector)
            KeywordIndexBuilder().build(dataset.experts, artifacts.keyword)
            GraphIndexBuilder().build(dataset.experts, artifacts.graph)

            platform = create_production_platform(artifacts, embedding)
            planner = RuleBasedPlanner(platform.retrievers.capabilities())
            query = Query("Find healthcare experts with Azure AI experience", top_k=3)
            result = platform.runtime.execute(query, planner.plan(query))
            self.assertTrue(result.items)
            self.assertTrue((artifacts.vector / "index.faiss").exists())
            self.assertTrue((artifacts.keyword / "keyword_index.json").exists())
            self.assertTrue((artifacts.graph / "graph.pkl").exists())
            self.assertEqual([entry.name for entry in platform.providers.discover()], ["networkx_graph"])

    def test_benchmark_sources_are_independent_of_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = generate_benchmark_dataset(temporary_directory, size=200)
            self.assertEqual(len(dataset.experts), 200)
            self.assertEqual(len(load_experts(temporary_directory)), 200)
            self.assertTrue((Path(temporary_directory) / "knowledge" / "relationships.json").exists())

    def test_evaluation_includes_ndcg_and_latency(self) -> None:
        items = (
            ResultItem("a", "expert", "Ada", "Healthcare AI"),
            ResultItem("b", "expert", "Ben", "Payments"),
        )
        result = RetrievalResult(items, "plan", "dense", 7.0)
        metrics = evaluate(result, {"a"}, k=2)
        self.assertEqual(metrics.ndcg_at_k, 1.0)
        self.assertEqual(metrics.latency_ms, 7.0)

    def test_ollama_client_validates_and_returns_structured_data(self) -> None:
        client = OllamaStructuredLLMClient("local-model", session=FakeSession())
        response = client.complete(prompt="Return a plan")
        self.assertEqual(response["strategy"], "dense")


if __name__ == "__main__":
    unittest.main()
