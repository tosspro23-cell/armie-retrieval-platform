from __future__ import annotations

import sys
from pathlib import Path
import unittest
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval import ExecutionObservation, Query, ResultItem, RetrievalRuntime
from armie_retrieval.evaluation import evaluate
from armie_retrieval.learning import LearningEngine, ObservationStore, PolicyRepository
from armie_retrieval.planners import LLMPlanner, RuleBasedPlanner
from armie_retrieval.processors import DeduplicateProcessor, ExpertRerankProcessor, MetadataFilterProcessor
from armie_retrieval.providers import InMemoryKnowledgeProvider, NetworkXKnowledgeGraphProvider
from armie_retrieval.providers.knowledge_graph import nx
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry
from armie_retrieval.retrievers import DenseRetriever, GraphRetriever, HybridRetriever, SparseRetriever


ITEMS = (
    ResultItem("a", "expert", "Ada", "Azure AI retrieval for healthcare", {"industry": "healthcare", "skills": "Azure AI, retrieval", "organization": "Hospital", "technology": "Azure AI Search", "projects": "Clinical Search"}),
    ResultItem("b", "expert", "Ben", "Fintech payments platform", {"industry": "fintech", "skills": "payments", "organization": "Fintech", "technology": "SQL", "projects": "Payments"}),
)


class StubLLM:
    def complete(self, *, prompt: str) -> Mapping[str, Any]:
        return {"strategy": "dense", "processors": ["deduplicate", "expert_rerank"], "top_k": 1, "constraints": {"latency_ms": 500}}


def runtime_for(items=ITEMS) -> tuple[RetrievalRuntime, RetrieverRegistry]:
    provider = InMemoryKnowledgeProvider(items)
    dense, sparse = DenseRetriever(provider), SparseRetriever(provider)
    retrievers = RetrieverRegistry()
    retrievers.register("dense", dense, capabilities={"dense"}, version="0.2.0", priority=80)
    retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"}, version="0.2.0", priority=100)
    processors = ProcessorRegistry()
    for processor in (DeduplicateProcessor(), MetadataFilterProcessor(), ExpertRerankProcessor()):
        processors.register(processor.name, processor, capabilities={processor.name}, version="0.2.0")
    return RetrievalRuntime(retrievers, processors), retrievers


class RetrievalMvpTest(unittest.TestCase):
    def setUp(self) -> None:
        self.query = Query("Azure retrieval healthcare", filters={"industry": "healthcare"}, top_k=1)

    def test_rule_planner_returns_declarative_hybrid_plan(self) -> None:
        plan = RuleBasedPlanner(frozenset({"dense", "sparse", "hybrid"})).plan(self.query)
        self.assertEqual(plan.strategy, "hybrid")
        self.assertIn("metadata_filter", plan.processor_names)
        self.assertNotIn("provider", plan.parameters)

    def test_llm_planner_returns_same_domain_contract(self) -> None:
        plan = LLMPlanner(StubLLM(), frozenset({"dense", "hybrid"})).plan(self.query)
        self.assertEqual(plan.strategy, "dense")
        self.assertEqual(plan.top_k, 1)
        self.assertEqual(plan.constraints["latency_ms"], 500)

    def test_same_runtime_executes_rule_and_llm_plans(self) -> None:
        runtime, retrievers = runtime_for()
        rule_plan = RuleBasedPlanner(retrievers.capabilities()).plan(self.query)
        llm_plan = LLMPlanner(StubLLM(), retrievers.capabilities()).plan(self.query)
        self.assertEqual(runtime.execute(self.query, rule_plan).items[0].id, "a")
        self.assertEqual(runtime.execute(self.query, llm_plan).items[0].id, "a")

    def test_registry_resolves_highest_priority_healthy_capability(self) -> None:
        registry = RetrieverRegistry()
        registry.register("slow", object(), capabilities={"dense"}, priority=1)
        fast = object()
        registry.register("fast", fast, capabilities={"dense"}, priority=10)
        self.assertIs(registry.resolve_capability("dense"), fast)
        registry.set_health("fast", "unhealthy")
        self.assertEqual(registry.discover(capability="dense")[0].name, "slow")

    def test_learning_publishes_policy_without_runtime_history_lookup(self) -> None:
        observations, policies = ObservationStore(), PolicyRepository()
        observations.append(ExecutionObservation("processor", "llm_judge", "unsupported_capability", {"processor": "llm_judge"}))
        policy = LearningEngine().optimize_and_publish(observations, policies)
        self.assertEqual(policy.version, 1)
        self.assertNotIn("llm_judge", policy.processor_defaults)
        self.assertIs(policies.latest(), policy)

    def test_evaluation_is_observational(self) -> None:
        runtime, retrievers = runtime_for()
        plan = RuleBasedPlanner(retrievers.capabilities()).plan(self.query)
        result = runtime.execute(self.query, plan)
        original = result.items
        metrics = evaluate(result, {"a"}, k=1)
        self.assertEqual(result.items, original)
        self.assertGreater(metrics.reciprocal_rank, 0)

    @unittest.skipUnless(nx is not None, "NetworkX is not installed in this environment")
    def test_graph_retriever_finds_related_expert(self) -> None:
        graph_provider = NetworkXKnowledgeGraphProvider.from_experts(ITEMS)
        graph = GraphRetriever(graph_provider)
        plan = RuleBasedPlanner(frozenset({"dense", "graph"})).plan(Query("Find experts connected to Azure AI", top_k=1))
        result = graph.retrieve(Query("Find experts connected to Azure AI", top_k=1), plan)
        self.assertEqual(result.items[0].id, "a")


if __name__ == "__main__":
    unittest.main()
