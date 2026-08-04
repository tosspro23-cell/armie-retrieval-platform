import unittest

from armie_retrieval.benchmarks import benchmark_metrics, gate4_profiles
from armie_retrieval.datasets import build_dataset, load_dataset
from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult, ResultItem
from armie_retrieval.observability import trace_query
from armie_retrieval.relevance import generate_benchmark_queries
from armie_retrieval.benchmarks.relevance import audit_dataset, audit_tier, grade_map, select_gold_queries


class Gate5ContractTests(unittest.TestCase):
    def test_gold_silver_tiers_are_stratified_and_non_overlapping(self):
        queries = generate_benchmark_queries()
        gold = select_gold_queries(queries)
        self.assertEqual(len(gold), 35)
        self.assertEqual(len({query.query_id for query in gold}), 35)
        self.assertEqual({query.category.value for query in gold}, {query.category.value for query in queries})
        self.assertEqual(len(set(query.query_id for query in queries) - {query.query_id for query in gold}), 85)

    def test_hand_calculated_binary_and_graded_metrics(self):
        class J:
            def __init__(self, grade, violated=()): self.grade, self.violated_constraints = grade, violated
        judgements = {"a": J(3), "b": J(2), "c": J(0), "d": J(0)}
        metrics = benchmark_metrics(["a", "c", "b", "d"], judgements)
        self.assertEqual(metrics["precision_at_5"], 0.4)  # two relevant items in a five-slot denominator
        self.assertEqual(metrics["recall_at_10"], 1.0)
        self.assertEqual(metrics["recall_at_10_grade_ge_2"], 1.0)
        self.assertEqual(metrics["grade_3_hit_at_10"], 1)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertEqual(metrics["grade_3_hit_rate"], 1)
        self.assertEqual(metrics["hard_negative_intrusion_rate"], 1)
        self.assertEqual(metrics["relevant_count_grade_ge_1"], 2)
        self.assertEqual(metrics["relevant_count_grade_ge_2"], 2)
        no_grade3 = benchmark_metrics(["b", "c"], {"b": J(2), "c": J(0)})
        self.assertEqual(no_grade3["grade_3_hit_at_10"], 0)
        self.assertEqual(no_grade3["no_grade_3_result"], 1)

    def test_audit_and_independent_judgements_include_review_evidence(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            build_dataset(root, size=12)
            profiles = load_dataset(root)
        query = select_gold_queries(generate_benchmark_queries())[0]
        judgements = grade_map(query, profiles, tier="gold")
        audit = audit_dataset(profiles, (query,), judgements)
        self.assertEqual(audit["profile_count"], 12)
        self.assertTrue(all(judgement.evidence_references for judgement in judgements.values()))
        self.assertTrue(all(judgement.review_status == "gold_reviewed" for judgement in judgements.values()))

    def test_gate4_profiles_keep_candidate_boundaries(self):
        profiles = {profile.profile_id: profile for profile in gate4_profiles()}
        self.assertEqual((profiles["H4"].retrieval_candidate_k, profiles["H4"].fusion_candidate_k, profiles["H4"].rerank_candidate_k, profiles["H4"].final_top_k), (100, 100, 30, 5))

    def test_silver_retains_rule_assisted_status_and_tier_audit(self):
        with __import__("tempfile").TemporaryDirectory() as root:
            build_dataset(root, size=12)
            profiles = load_dataset(root)
        query = select_gold_queries(generate_benchmark_queries())[0]
        silver = grade_map(query, profiles, tier="silver")
        audit = audit_tier(profiles, (query,), {query.query_id: silver})
        self.assertTrue(all(judgement.review_status == "silver_rule_assisted" for judgement in silver.values()))
        self.assertEqual(audit["review_status_counts"], {"silver_rule_assisted": len(profiles)})

    def test_trace_end_to_end_is_not_lower_than_observed_stage_latencies(self):
        class Planner:
            def plan(self, query):
                return RetrievalPlan("dense", top_k=1)

        class Retriever:
            name = "fixture_dense"

            def retrieve(self, query, plan):
                import time
                started = time.perf_counter()
                time.sleep(0.003)
                return RetrievalResult((ResultItem("x", "expert", "x", "x"),), plan.plan_id, plan.strategy, (time.perf_counter() - started) * 1000, provenance={"fusion_latency_ms": 0.0005})

        class Runtime:
            def execute_with_trace(self, query, plan, collector):
                retriever = Retriever()
                result = retriever.retrieve(query, plan)
                collector.record_retrieval(retriever, result)
                collector.record_final(result)
                return result

        _, trace = trace_query(Runtime(), Planner(), Query("x"))
        timing = trace.timing_ms
        self.assertGreaterEqual(timing["end_to_end"], timing["retrieval"])
        self.assertGreaterEqual(timing["end_to_end"], timing["fusion"])
        self.assertGreaterEqual(timing["end_to_end"], timing["reranking"])


if __name__ == "__main__":
    unittest.main()
