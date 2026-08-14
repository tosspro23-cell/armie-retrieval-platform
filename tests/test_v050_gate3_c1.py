import unittest

from armie_retrieval.contracts import Constraint, ConstraintCategory, ConstraintOperator, RetrievalContract, TemporalConstraint, TemporalOperator
from armie_retrieval.models import Query, RetrievalPlan
from armie_retrieval.providers.elasticsearch.retrievers import ElasticsearchDenseRetriever
from armie_retrieval.retrievers.c2_postfilter import C2PostFilterRetriever


class _Response:
    def __init__(self, body): self._body = body
    def json(self): return self._body


class _Client:
    def __init__(self, hits): self.hits = hits; self.payloads = []
    def request(self, method, path, **kwargs):
        self.payloads.append(kwargs["json"])
        return _Response({"hits": {"hits": self.hits}})


class _Embedding:
    def embed(self, texts): return [[0.1, 0.2] for _ in texts]


def _hit(identifier, years=21, industry="Energy", seniority="senior", rank=2):
    return {"_id": identifier, "_score": float(rank), "_source": {"display_name": identifier, "summary": identifier, "years_experience": years, "industries": [industry], "seniority": seniority, "seniority_rank": rank}}


class Gate3C1Tests(unittest.TestCase):
    def test_c0_no_contract_is_unfiltered_and_c1_identity_is_explicit(self):
        client = _Client([_hit("A")])
        retriever = ElasticsearchDenseRetriever(client, index="armie-v05-dense", embedding_provider=_Embedding())
        result = retriever.retrieve(Query("semantic query"), RetrievalPlan(strategy="dense", top_k=5))
        self.assertEqual(result.provenance["strategy_identity"], "C0")
        self.assertNotIn("filter", client.payloads[0]["knn"])

    def test_c1_years_filter_is_native_and_does_not_backfill(self):
        client = _Client([_hit("D", 21), _hit("E", 27)])
        retriever = ElasticsearchDenseRetriever(client, index="armie-v05-dense", embedding_provider=_Embedding())
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC),))
        result = retriever.retrieve(Query("semantic query", top_k=5, retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5))
        self.assertEqual(result.provenance["strategy_identity"], "C1")
        self.assertEqual(result.provenance["constraint_diagnostics"]["strict_shortfall_count"], 3)
        self.assertEqual(client.payloads[0]["knn"]["filter"], {"bool": {"filter": [{"range": {"years_experience": {"gte": 20}}}]}})

    def test_c1_combined_and_exclusion_polarity(self):
        client = _Client([_hit("A")])
        retriever = ElasticsearchDenseRetriever(client, index="armie-v05-dense", embedding_provider=_Embedding())
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Energy", category=ConstraintCategory.CATEGORICAL),), exclusions=(Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Banking", category=ConstraintCategory.CATEGORICAL),))
        retriever.retrieve(Query("x", retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5))
        filters = client.payloads[0]["knn"]["filter"]["bool"]["filter"]
        self.assertIn({"term": {"industries": "Energy"}}, filters)
        self.assertIn({"bool": {"must_not": [{"term": {"industries": "Banking"}}]}}, filters)

    def test_deferred_hard_constraint_is_non_executable(self):
        client = _Client([_hit("A")])
        retriever = ElasticsearchDenseRetriever(client, index="armie-v05-dense", embedding_provider=_Embedding())
        contract = RetrievalContract(semantic_query="x", temporal_constraints=(TemporalConstraint(operator=TemporalOperator.AFTER, start=__import__("datetime").date(2020, 1, 1)),))
        result = retriever.retrieve(Query("x", retrieval_contract=contract), RetrievalPlan(strategy="dense", top_k=5))
        self.assertEqual(result.items, ())
        self.assertEqual(client.payloads, [])
        self.assertEqual(result.provenance["constraint_diagnostics"]["validation_state"], "NON_EXECUTABLE")


if __name__ == "__main__": unittest.main()
