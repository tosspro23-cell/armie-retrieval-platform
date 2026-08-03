import tempfile
import unittest
from pathlib import Path

from armie_retrieval.benchmarks import FailureCode, classify_failure, default_profiles, graded_metrics
from armie_retrieval.datasets import build_dataset, load_dataset, validate_dataset
from armie_retrieval.indexing.elasticsearch import build_index_name, build_mapping
from armie_retrieval.relevance import draft_judgements, generate_benchmark_queries


class V040FoundationTests(unittest.TestCase):
    def test_dataset_is_deterministic_and_checksum_validated(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            left = build_dataset(first, size=25)
            right = build_dataset(second, size=25)
            self.assertEqual(left.checksum, right.checksum)
            self.assertEqual(left.record_count, 25)
            self.assertEqual(validate_dataset(first).checksum, left.checksum)
            self.assertEqual(len(load_dataset(first)), 25)
            self.assertTrue(load_dataset(first)[0].search_document)

    def test_query_taxonomy_has_120_cases_and_draft_judgements_are_reviewable(self):
        with tempfile.TemporaryDirectory() as root:
            build_dataset(root, size=15)
            queries = generate_benchmark_queries()
            judgements = draft_judgements(queries, load_dataset(root))
            self.assertEqual(len(queries), 120)
            self.assertEqual(len({query.category for query in queries}), 10)
            self.assertEqual(len(judgements), 120 * 15)
            self.assertTrue(all(judgement.review_status == "draft" for judgement in judgements))

    def test_graded_metrics_and_failure_taxonomy(self):
        metrics = graded_metrics(["a", "b", "c"], {"a": 3, "b": 0, "c": 1}, k=3)
        self.assertEqual(metrics["grade_3_hit"], 1)
        self.assertGreater(metrics["ndcg_at_k"], 0)
        self.assertIn(FailureCode.semantic_false_positive, classify_failure("semantic query", ["x"], {"x": 0}, stage="dense"))

    def test_elasticsearch_mapping_is_versioned_and_score_semantics_are_explicit(self):
        mapping = build_mapping(embedding_dimensions=4)
        self.assertEqual(mapping["mappings"]["_meta"]["mapping_version"], "expert-discovery-es-mapping-v1")
        self.assertEqual(mapping["mappings"]["properties"]["embedding"]["dims"], 4)
        self.assertEqual(build_index_name("abc-123"), "armie-experts-v1-abc-123")
        with self.assertRaises(ValueError):
            build_index_name("../bad")

    def test_required_profiles_are_declared(self):
        profiles = {profile.profile_id: profile for profile in default_profiles()}
        self.assertEqual(set(profiles), {"p1", "p2", "p3", "p4", "p5", "p6"})
        self.assertEqual(profiles["p6"].reranker, "bge_cross_encoder")
        self.assertEqual((profiles["p6"].retrieval_candidate_k, profiles["p6"].rerank_candidate_k, profiles["p6"].final_top_k), (100, 30, 5))


if __name__ == "__main__":
    unittest.main()
