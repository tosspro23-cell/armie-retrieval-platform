from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.models import Query, ResultItem
from armie_retrieval.observability import export_trace, render_terminal, trace_query
from armie_retrieval.planners import LLMPlanner, RuleBasedPlanner
from armie_retrieval.processors import DeduplicateProcessor, ExpertRerankProcessor, MetadataFilterProcessor
from armie_retrieval.providers import InMemoryKnowledgeProvider, NetworkXKnowledgeGraphProvider
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry
from armie_retrieval.retrievers import DenseRetriever, GraphRetriever, HybridRetriever, SparseRetriever
from armie_retrieval.runtime import RetrievalRuntime


ITEMS = (
    ResultItem("expert-001", "expert", "Ada", "Azure AI retrieval for healthcare", {"industry": "healthcare", "skills": "Azure AI, retrieval", "organization": "Northstar", "technology": "Azure AI", "projects": "Clinical Search"}),
    ResultItem("expert-002", "expert", "Ben", "RAG systems for financial services", {"industry": "financial services", "skills": "RAG", "organization": "Atlas", "technology": "RAG", "projects": "Risk Search"}),
    ResultItem("expert-003", "expert", "Cara", "Healthcare knowledge graph expert", {"industry": "healthcare", "skills": "knowledge graph", "organization": "Northstar", "technology": "knowledge graph", "projects": "Care Graph"}),
)


class InvalidStrategyClient:
    def complete(self, *, prompt: str) -> Mapping[str, Any]:
        return {"strategy": "unsupported", "processors": ["deduplicate"], "top_k": 2}


def make_runtime() -> tuple[RetrievalRuntime, RetrieverRegistry]:
    provider = InMemoryKnowledgeProvider(ITEMS)
    dense, sparse = DenseRetriever(provider), SparseRetriever(provider)
    graph = GraphRetriever(NetworkXKnowledgeGraphProvider.from_experts(ITEMS))
    retrievers = RetrieverRegistry()
    retrievers.register("dense", dense, capabilities={"dense"}, version="0.2.2")
    retrievers.register("keyword", sparse, capabilities={"sparse"}, version="0.2.2")
    retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"}, version="0.2.2")
    retrievers.register("graph", graph, capabilities={"graph"}, version="0.2.2")
    processors = ProcessorRegistry()
    for processor in (DeduplicateProcessor(), MetadataFilterProcessor(), ExpertRerankProcessor()):
        processors.register(processor.name, processor, capabilities={processor.name}, version="0.2.2")
    return RetrievalRuntime(retrievers, processors), retrievers


class ObservabilityV022Test(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime, self.retrievers = make_runtime()
        self.query = Query("Find healthcare experts with Azure AI", top_k=2)

    def test_trace_is_json_serializable_and_round_trips_to_mapping(self) -> None:
        _, trace = trace_query(
            self.runtime, RuleBasedPlanner(self.retrievers.capabilities()), self.query,
            query_id="healthcare-azure", relevant_ids={"expert-001"},
        )
        payload = trace.to_json()
        parsed = trace.from_json(payload)
        self.assertEqual(parsed["query_id"], "healthcare-azure")
        self.assertIn("planner", parsed)
        self.assertIn("ranking", parsed)

    def test_trace_does_not_change_normal_retrieval_results(self) -> None:
        planner = RuleBasedPlanner(self.retrievers.capabilities())
        plan = planner.plan(self.query)
        baseline = self.runtime.execute(self.query, plan)
        traced, trace = trace_query(self.runtime, planner, self.query)
        self.assertEqual([(item.id, item.score) for item in baseline.items], [(item.id, item.score) for item in traced.items])
        self.assertEqual(trace.planner.selected_strategy, plan.strategy)

    def test_hybrid_trace_preserves_per_retriever_fusion_contributions(self) -> None:
        _, trace = trace_query(self.runtime, RuleBasedPlanner(self.retrievers.capabilities()), self.query)
        self.assertIsNotNone(trace.fusion)
        assert trace.fusion is not None
        self.assertEqual(trace.fusion.method, "reciprocal_rank_fusion")
        self.assertTrue(any(candidate.contributions for candidate in trace.fusion.candidates))
        self.assertEqual([item.rank for item in trace.ranking.candidates], [1, 2])

    def test_graph_trace_includes_real_graph_relationship_evidence(self) -> None:
        planner = RuleBasedPlanner(self.retrievers.capabilities())
        graph_query = Query("Find healthcare experts connected to Azure AI", top_k=2)
        _, trace = trace_query(self.runtime, planner, graph_query)
        graph = next(item for item in trace.retrievers if item.name == "graph")
        self.assertTrue(graph.candidates)
        self.assertTrue(any("HAS_" in evidence for candidate in graph.candidates for evidence in candidate.evidence))

    def test_evaluation_trace_explains_hits_misses_and_metric_inputs(self) -> None:
        _, trace = trace_query(
            self.runtime, RuleBasedPlanner(self.retrievers.capabilities()), self.query,
            query_id="case", relevant_ids={"expert-001", "missing-expert"},
        )
        assert trace.ground_truth is not None and trace.evaluation is not None
        self.assertIn("missing-expert", trace.ground_truth.missed_relevant_ids)
        self.assertIn("ndcg", trace.evaluation.calculation)
        self.assertEqual(len(trace.evaluation.calculation["relevance_vector"] if "relevance_vector" in trace.evaluation.calculation else trace.evaluation.calculation["ndcg"]["relevance_vector"]), 2)

    def test_zero_relevant_and_empty_retrieval_are_explicit(self) -> None:
        base_plan = RuleBasedPlanner(self.retrievers.capabilities()).plan(Query("unmatchabletoken", top_k=2))
        class SparseOnlyPlanner:
            def plan(self, query):
                return replace(base_plan, strategy="sparse")
        _, trace = trace_query(
            self.runtime, SparseOnlyPlanner(), Query("unmatchabletoken", top_k=2),
            relevant_ids=set(),
        )
        assert trace.evaluation is not None and trace.ground_truth is not None
        self.assertEqual(trace.ranking.candidates, ())
        self.assertEqual(trace.evaluation.metrics["recall_at_k"], 0.0)
        self.assertEqual(trace.ground_truth.first_relevant_rank, None)

    def test_llm_planner_trace_captures_structured_output_and_fallback(self) -> None:
        planner = LLMPlanner(InvalidStrategyClient(), self.retrievers.capabilities())
        _, trace = trace_query(self.runtime, planner, self.query)
        self.assertEqual(trace.planner.raw_output["strategy"], "unsupported")
        self.assertIsNotNone(trace.planner.fallback)

    def test_ablation_modes_and_export_and_rendering(self) -> None:
        base = RuleBasedPlanner(self.retrievers.capabilities()).plan(self.query)
        for strategy in ("dense", "sparse", "graph", "hybrid"):
            class FixedPlanner:
                def plan(self, query):
                    return replace(base, strategy=strategy)
            _, trace = trace_query(self.runtime, FixedPlanner(), self.query)
            self.assertEqual(trace.planner.selected_strategy, strategy)
            self.assertIn("Final Ranking", render_terminal(trace))
            self.assertIn("Dense Retrieval", render_terminal(trace, verbose=True))
        with tempfile.TemporaryDirectory() as temporary_directory:
            _, trace = trace_query(self.runtime, RuleBasedPlanner(self.retrievers.capabilities()), self.query)
            export = export_trace(trace, temporary_directory)
            self.assertTrue(export.exists())
            self.assertEqual(trace.from_json(export.read_text())["schema_version"], "0.2.3")


if __name__ == "__main__":
    unittest.main()
