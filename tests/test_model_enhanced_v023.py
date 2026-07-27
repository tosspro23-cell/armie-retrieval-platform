from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).parents[1] / "examples"))

from armie_retrieval.evaluation import evaluate_at_cutoffs
from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult, ResultItem
from armie_retrieval.observability import trace_query
from armie_retrieval.observability.render import render_terminal
from armie_retrieval.planners import LLMPlanner, RuleBasedPlanner
from armie_retrieval.planners.llm import PlannerStructuredOutputError
from armie_retrieval.planners.metadata import planner_metadata, routing_warnings
from armie_retrieval.processors import DeduplicateProcessor, QueryAwareRerankProcessor
from armie_retrieval.profiles import ProfileError, apply_overrides, load_profile
from armie_retrieval.providers import InMemoryKnowledgeProvider
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry
from armie_retrieval.rerankers import BGECrossEncoderReranker, MetadataBoostReranker, NoOpReranker, RerankerPrerequisiteError
from armie_retrieval.retrievers import DenseRetriever, HybridRetriever, SparseRetriever
from armie_retrieval.runtime import RetrievalRuntime
from armie_retrieval.runtime_profiles import select_planner, select_reranker
from planner_ablation import summarize


ITEMS = (
    ResultItem("one", "expert", "Ada", "Healthcare Azure AI retrieval", {"industry": "healthcare", "skills": "Azure AI"}),
    ResultItem("two", "expert", "Ben", "Financial RAG systems", {"industry": "finance", "skills": "RAG"}),
    ResultItem("three", "expert", "Cara", "Healthcare knowledge graph", {"industry": "healthcare", "skills": "graph"}),
)


def runtime_with(provider):
    source = InMemoryKnowledgeProvider(ITEMS)
    dense, sparse = DenseRetriever(source), SparseRetriever(source)
    retrievers = RetrieverRegistry()
    retrievers.register("dense", dense, capabilities={"dense"})
    retrievers.register("sparse", sparse, capabilities={"sparse"})
    retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"})
    processor = QueryAwareRerankProcessor(provider, name="rerank")
    processors = ProcessorRegistry()
    processors.register("deduplicate", DeduplicateProcessor(), capabilities={"deduplicate"})
    processors.register("rerank", processor, capabilities={"rerank"})
    return RetrievalRuntime(retrievers, processors), retrievers, processor


class MockCrossEncoder:
    def predict(self, pairs, batch_size, show_progress_bar=False):
        return [10.0 if "Cara" in document else float(index) for index, (_, document) in enumerate(pairs)]


class FailingClient:
    def complete(self, *, prompt):
        raise RuntimeError("Ollama unavailable")


class MetadataClient:
    def complete(self, *, prompt):
        return {
            "strategy": "dense", "retrievers": ["dense"], "processors": ["deduplicate", "rerank"], "top_k": 5,
            "skills": ["Azure AI"], "industries": ["healthcare"], "organizations": [],
            "reason_codes": ["semantic_similarity_required", "invalid_code"], "constraint_types": ["skill", "industry", "invalid_type"],
        }


class ModelEnhancedV023Test(unittest.TestCase):
    def test_all_profiles_and_cli_override_resolution(self):
        self.assertEqual(load_profile("fixture")["planner"]["type"], "rule")
        self.assertEqual(load_profile("baseline")["embedding"]["model"], "BAAI/bge-m3")
        model = load_profile("model-enhanced")
        override = apply_overrides(model, planner={"type": "rule-based"}, reranker={"type": "none"})
        self.assertEqual(override["planner"]["type"], "rule-based")
        self.assertEqual(override["reranker"]["type"], "none")
        with self.assertRaises(ProfileError):
            load_profile("missing")

    def test_ollama_selection_has_controlled_rule_fallback(self):
        profile = load_profile("model-enhanced")
        selection = select_planner(profile, capabilities=frozenset({"dense", "sparse", "hybrid"}), llm_client=FailingClient())
        plan = selection.planner.plan(Query("Find healthcare experts", top_k=5))
        self.assertEqual(plan.strategy, "hybrid")
        self.assertEqual(selection.planner.last_fallback_reason, "Ollama unavailable")

    def test_reranker_providers_and_bounded_candidate_pool(self):
        self.assertEqual(NoOpReranker().rerank(Query("x"), ITEMS, 2).provider, "none")
        boosted = MetadataBoostReranker().rerank(Query("x", filters={"industry": "healthcare"}), ITEMS, 3)
        self.assertEqual(boosted.items[0].item.id, "one")
        bge = BGECrossEncoderReranker(model=MockCrossEncoder(), batch_size=2)
        output = bge.rerank(Query("healthcare"), ITEMS, 2)
        self.assertEqual(output.items[0].item.id, "three")
        self.assertEqual(len(output.items), 2)

    def test_candidate_pool_final_top_k_and_rerank_trace_are_separate(self):
        runtime, retrievers, processor = runtime_with(MetadataBoostReranker())
        processor.selection = type("Selection", (), {"requested": "metadata_boost", "actual": "metadata_boost", "fallback_reason": None})()
        planner = RuleBasedPlanner(retrievers.capabilities())
        query = Query("healthcare azure", filters={"industry": "healthcare"}, top_k=1)
        plan = RetrievalPlan("hybrid", ("deduplicate", "rerank"), 1, query.filters, parameters={"retrieval_candidate_k": 3, "rerank_candidate_k": 2, "final_top_k": 1})

        class FixedPlanner:
            def plan(self, ignored): return plan

        result, trace = trace_query(runtime, FixedPlanner(), query)
        self.assertEqual(len(result.items), 1)
        self.assertIsNotNone(trace.reranking)
        assert trace.reranking is not None
        self.assertEqual(trace.reranking.candidate_count_in, 2)
        self.assertEqual(trace.reranking.final_candidate_count, 1)
        self.assertTrue(trace.processor_stages[-1].truncated)

    def test_multi_k_metrics_explain_theoretical_precision_maximum(self):
        result = RetrievalResult(ITEMS, "plan", "dense", 1.0)
        metrics, arithmetic = evaluate_at_cutoffs(result, {"one", "two"}, (1, 2, 5))
        self.assertEqual(metrics["precision_at_5"], 0.4)
        self.assertEqual(arithmetic["cutoffs"]["5"]["maximum_possible_precision"], 0.4)
        self.assertIn("2/5", arithmetic["cutoffs"]["5"]["note"])

    def test_bge_selection_falls_back_without_cached_model(self):
        selection = select_reranker({"reranker": {"type": "bge", "model": "not/a-real-local-model", "fallback": "metadata_boost"}})
        self.assertEqual(selection.requested, "bge_cross_encoder")
        self.assertEqual(selection.actual, "metadata_boost")
        self.assertIsNotNone(selection.fallback_reason)

    def test_structured_planner_metadata_and_routing_warning_are_observable(self):
        runtime, retrievers, _ = runtime_with(MetadataBoostReranker())
        planner = LLMPlanner(MetadataClient(), retrievers.capabilities())
        _, trace = trace_query(runtime, planner, Query("Find healthcare experts with Azure AI experience", top_k=5))
        self.assertEqual(trace.planner.reason_codes, ("semantic_similarity_required",))
        self.assertEqual(trace.planner.constraint_types, ("skill", "industry"))
        self.assertIn("Planner extracted multiple graph-representable constraints but did not select graph.", trace.planner.warnings)
        self.assertIn("Planner selected dense-only despite exact lexical entities.", trace.planner.warnings)
        rendered = render_terminal(trace, verbose=True)
        self.assertIn("reason_codes=semantic_similarity_required", rendered)
        self.assertIn("available capabilities:", rendered)
        self.assertIn("routing warnings:", rendered)

    def test_routing_warnings_never_mutate_plan_or_flag_plain_semantic_dense(self):
        metadata, warnings = planner_metadata({"reason_codes": ["invalid"], "constraint_types": ["unknown"]}, Query("Find someone with relevant AI experience"))
        self.assertEqual(metadata["reason_codes"], ())
        self.assertTrue(warnings)
        self.assertEqual(routing_warnings(strategy="dense", selected_retrievers=("dense",), metadata=metadata), ())
        plan = RetrievalPlan("dense", (), 5)
        self.assertEqual(plan.strategy, "dense")

    def test_reranker_trace_records_all_scored_candidates_and_rank_convention(self):
        runtime, retrievers, processor = runtime_with(BGECrossEncoderReranker(model=MockCrossEncoder()))
        processor.selection = type("Selection", (), {"requested": "bge_cross_encoder", "actual": "bge_cross_encoder", "fallback_reason": None})()
        plan = RetrievalPlan("hybrid", ("rerank",), 2, parameters={"retrieval_candidate_k": 3, "rerank_candidate_k": 3, "final_top_k": 2})

        class FixedPlanner:
            def plan(self, ignored): return plan

        _, trace = trace_query(runtime, FixedPlanner(), Query("healthcare RAG", top_k=2))
        assert trace.reranking is not None
        self.assertEqual(trace.reranking.candidate_count_in, 3)
        self.assertEqual(trace.reranking.candidate_count_after_rerank, 3)
        self.assertEqual(len(trace.reranking.candidates), 3)
        cara = next(row for row in trace.reranking.candidates if row["expert_id"] == "three")
        self.assertEqual(cara["rank_change"], cara["reranker_rank"] - cara["pre_rerank_rank"])
        self.assertEqual(cara["rank_improvement"], cara["pre_rerank_rank"] - cara["reranker_rank"])
        self.assertNotIn("fusion_rank", cara)
        self.assertIn("Rank changes:", render_terminal(trace, verbose=True))

    def test_trace_order_aliases_and_provider_neutral_metadata_fields(self):
        runtime, retrievers, processor = runtime_with(MetadataBoostReranker())
        processor.selection = type("Selection", (), {"requested": "metadata_boost", "actual": "metadata_boost", "fallback_reason": None})()
        plan = RetrievalPlan("hybrid", ("rerank",), 1, parameters={"retrieval_candidate_k": 3, "rerank_candidate_k": 2, "final_top_k": 1})
        class FixedPlanner:
            def plan(self, ignored): return plan
        _, trace = trace_query(runtime, FixedPlanner(), Query("healthcare azure", top_k=1))
        rendered = render_terminal(trace)
        self.assertLess(rendered.index("7. Reranking"), rendered.index("8. Final Ranking"))
        self.assertIn("metadata_candidates_processed=2", rendered)
        self.assertNotIn("cross_encoder_scored", rendered)
        self.assertEqual(routing_warnings(strategy="sparse", selected_retrievers=("keyword",), metadata={"requested_retrievers": ("sparse",), "reason_codes": (), "constraint_types": ()}), ())

    def test_structured_planner_validation_reports_actionable_field(self):
        class InvalidFilters:
            def complete(self, *, prompt): return {"strategy": "dense", "processors": ["rerank"], "filters": []}
        with self.assertRaises(PlannerStructuredOutputError) as captured:
            LLMPlanner(InvalidFilters(), frozenset({"dense"})).plan(Query("x"))
        self.assertEqual(captured.exception.diagnostic["fallback_field"], "filters")
        self.assertEqual(captured.exception.diagnostic["expected_type"], "object")

    def test_ablation_summary_requires_stronger_repeated_evidence_before_default_change(self):
        template = {
            "plan_valid": True, "actual_provider": "ollama", "routing_warnings": [],
            "metrics": {"precision_at_k": 0.4, "recall_at_k": 1.0, "reciprocal_rank": 1.0, "ndcg_at_k": 1.0}, "labelled": True,
        }
        small = {**template, "model": "qwen3:4b", "planner_latency_ms": 100.0}
        large = {**template, "model": "qwen3:8b", "planner_latency_ms": 300.0}
        summary = summarize([small, large])
        self.assertEqual(summary["recommendation"], "keep qwen3:4b default")
        self.assertEqual(summary["per_model"]["qwen3:4b"]["plan_valid_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
