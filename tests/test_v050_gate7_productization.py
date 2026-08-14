import unittest

from armie_retrieval.constraints import registry_snapshot
from armie_retrieval.contracts import Constraint, ConstraintCategory, ConstraintOperator, RetrievalContract, TemporalConstraint, TemporalOperator
from armie_retrieval.models import Query, RetrievalPlan
from armie_retrieval.providers.elasticsearch.retrievers import ElasticsearchDenseRetriever
from armie_retrieval.indexing.elasticsearch import ElasticsearchClient


class Response:
    def __init__(self, body): self.body = body
    def json(self): return self.body


class Client:
    def __init__(self, hits): self.hits, self.calls = hits, []
    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs.get("json")))
        return Response({"hits": {"hits": self.hits}})


class Embedding:
    def embed(self, texts): return [[0.1, 0.2] for _ in texts]


def hit(identifier, score=1.0):
    return {"_id": identifier, "_score": score, "_source": {"display_name": identifier, "summary": identifier}}


class Gate7ProductizationTests(unittest.TestCase):
    def test_registry_is_authoritative_without_backend_dsl(self):
        snapshot = registry_snapshot()
        self.assertEqual(snapshot["version"], "v0.5-c1-capability-registry-1")
        self.assertIn("years_experience", snapshot["supported"])
        self.assertIn("gte", snapshot["supported"]["years_experience"]["operators"])
        self.assertNotIn("dsl", snapshot["supported"]["years_experience"])

    def test_c0_payload_and_identity_remain_unfiltered(self):
        client = Client([hit(str(i)) for i in range(10)])
        result = ElasticsearchDenseRetriever(client, index="test", embedding_provider=Embedding()).retrieve(Query("x"), RetrievalPlan(strategy="dense", top_k=5))
        self.assertEqual(result.provenance["strategy_identity"], "C0")
        self.assertEqual(len(result.items), 5)
        self.assertEqual(result.provenance["candidate_pool_count"], 10)
        self.assertEqual(result.provenance["returned_k"], 5)
        self.assertNotIn("filter", client.calls[0][2]["knn"])

    def test_c1_candidate_pool_is_not_exposed_as_final_results(self):
        client = Client([hit(str(i)) for i in range(10)])
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC),))
        result = ElasticsearchDenseRetriever(client, index="test", embedding_provider=Embedding()).retrieve(Query("x", retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5, parameters={"retrieval_candidate_k": 100}))
        self.assertLessEqual(len(result.items), 5)
        self.assertEqual(result.provenance["candidate_pool_count"], 10)
        self.assertEqual(result.provenance["eligible_candidate_count"], 10)
        self.assertEqual(result.provenance["returned_k"], 5)
        self.assertEqual(result.provenance["shortfall"]["count"], 0)

    def test_supported_contract_is_c1_with_semantic_trace_and_shortfall(self):
        client = Client([hit("A")])
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC),))
        result = ElasticsearchDenseRetriever(client, index="test", embedding_provider=Embedding()).retrieve(Query("x", retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5))
        diagnostics = result.provenance["constraint_diagnostics"]
        self.assertEqual(result.provenance["strategy_identity"], "C1")
        self.assertEqual(diagnostics["validation_state"], "VALID")
        self.assertEqual(diagnostics["constraint_trace"][0]["canonical_field"], "years_experience")
        self.assertEqual(diagnostics["shortfall"]["count"], 4)

    def test_unsupported_contract_does_not_call_backend(self):
        client = Client([hit("A")])
        contract = RetrievalContract(semantic_query="x", temporal_constraints=(TemporalConstraint(operator=TemporalOperator.AFTER, start=__import__("datetime").date(2020, 1, 1)),))
        result = ElasticsearchDenseRetriever(client, index="test", embedding_provider=Embedding()).retrieve(Query("x", retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5))
        self.assertEqual(client.calls, [])
        self.assertEqual(result.provenance["constraint_diagnostics"]["error_category"], "UNSUPPORTED_CONSTRAINT")

    def test_real_adapter_rejects_incompatible_projection_before_search(self):
        class RealClient(ElasticsearchClient):
            def __init__(self): super().__init__(base_url="http://unused")
            def request(self, method, path, **kwargs):
                if method == "GET":
                    return Response({"test": {"mappings": {"_meta": {}, "properties": {"embedding": {"dims": 2}}}}})
                raise AssertionError("search must not execute")
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Energy", category=ConstraintCategory.CATEGORICAL),))
        result = ElasticsearchDenseRetriever(RealClient(), index="old-index", embedding_provider=Embedding()).retrieve(Query("x", retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5))
        self.assertEqual(result.items, ())
        self.assertEqual(result.provenance["error_category"], "INDEX_INCOMPATIBLE")
        self.assertEqual(result.provenance["contract_state"], "INDEX_INCOMPATIBLE")


if __name__ == "__main__":
    unittest.main()
