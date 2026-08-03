import unittest

from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult, ResultItem
from armie_retrieval.observability import capture_plan
from armie_retrieval.planners import RuleBasedPlanner
from armie_retrieval.processors import QueryAwareRerankProcessor
from armie_retrieval.providers.elasticsearch import ElasticsearchHybridRetriever
from armie_retrieval.rerankers import BGECrossEncoderReranker


def item(identifier: str, score: float, source: str) -> ResultItem:
    return ResultItem(identifier, "expert", identifier, identifier, metadata={"source": source}, score=score, signals={source: score})


class _Child:
    def __init__(self, name: str, rows: tuple[ResultItem, ...]) -> None:
        self.name = name
        self._rows = rows

    def retrieve(self, query, plan):
        return RetrievalResult(self._rows, plan.plan_id, plan.strategy, 1.0, provenance={"provider": self.name, "score_type": f"{self.name}_score"})


class _FakeCrossEncoder:
    def predict(self, pairs, batch_size=8, show_progress_bar=False):
        return [float(int(pair[1].split("Expert: ", 1)[1].splitlines()[0])) for pair in pairs]


class Gate4ContractTests(unittest.TestCase):
    def test_rule_planner_profile_is_deterministic_and_plan_is_immutable(self):
        planner = RuleBasedPlanner(
            frozenset({"hybrid"}),
            strategy_override="hybrid",
            processor_names=("deduplicate", "rerank"),
            parameters={"retrieval_candidate_k": 100, "fusion_candidate_k": 100, "rerank_candidate_k": 30, "final_top_k": 5},
        )
        query = Query("Find experts with Elasticsearch experience", top_k=5)
        first, _ = capture_plan(planner, query)
        second, _ = capture_plan(planner, query)
        self.assertEqual(first.strategy, "hybrid")
        self.assertEqual(first.processor_names, ("deduplicate", "rerank"))
        self.assertEqual(first.parameters, second.parameters)
        with self.assertRaises(Exception):
            first.parameters["retrieval_candidate_k"] = 1  # type: ignore[index]

    def test_rrf_deduplicates_by_expert_id_and_preserves_source_semantics(self):
        dense = _Child("elasticsearch_dense", (item("a", 0.9, "dense"), item("b", 0.8, "dense")))
        sparse = _Child("elasticsearch_bm25", (item("a", 12.0, "bm25"), item("c", 8.0, "bm25")))
        retriever = ElasticsearchHybridRetriever(dense, sparse, rrf_k=60)
        plan = RetrievalPlan("hybrid", top_k=2, parameters={"retrieval_candidate_k": 2, "fusion_candidate_k": 3})
        result = retriever.retrieve(Query("x"), plan)
        self.assertEqual([row.id for row in result.items], ["a", "b", "c"])
        self.assertEqual(result.provenance["fusion_candidates"]["a"]["elasticsearch_bm25"]["source_score_semantic"], "elasticsearch_bm25_score")
        self.assertAlmostEqual(result.provenance["fusion_candidates"]["a"]["total_fused_score"], 1 / 61 + 1 / 61)

    def test_cross_encoder_receives_bounded_pool_and_records_rank_movement(self):
        provider = BGECrossEncoderReranker(model=_FakeCrossEncoder())
        processor = QueryAwareRerankProcessor(provider, name="rerank")
        plan = RetrievalPlan("dense", top_k=2, parameters={"rerank_candidate_k": 3, "final_top_k": 2})
        processor.bind_query(Query("x"))
        before = RetrievalResult(tuple(item(str(i), float(i), "dense") for i in range(5)), plan.plan_id, plan.strategy, 1.0)
        after = processor.process(before, plan)
        self.assertEqual(len(processor.last_input_items), 3)
        self.assertEqual(len(after.items), 2)
        self.assertEqual(processor.last_rerank_result.scored_items[0].input_rank, 3)
        self.assertEqual(processor.last_rerank_result.scored_items[0].output_rank, 1)
        self.assertEqual(processor.last_rerank_result.model_load_latency_ms, 0.0)
        self.assertGreaterEqual(processor.last_rerank_result.inference_latency_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
