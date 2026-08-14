import unittest
from types import MethodType

from armie_retrieval.application.workbench import WorkbenchService
from armie_retrieval.models import Query, ResultItem, RetrievalResult


class _C1Fake:
    def __init__(self, count=2):
        self.count = count
        self.calls = 0

    def retrieve(self, query, plan):
        self.calls += 1
        return RetrievalResult(
            items=tuple(ResultItem(str(i), "expert", f"Expert {i}", "summary", {"industry": "healthcare"}, 1.0, ("elasticsearch_dense",), {"elasticsearch_dense_score": 1.0}) for i in range(self.count)),
            plan_id=plan.plan_id,
            strategy=plan.strategy,
            latency_ms=12.0,
            provenance={
                "contract_state": "VALID",
                "strategy_identity": "C1",
                "runtime_strategy": "constraint_prefilter",
                "requested_k": plan.top_k,
                "returned_k": self.count,
                "shortfall": {"requested": plan.top_k, "returned": self.count, "count": max(0, plan.top_k - self.count), "reason": "STRICT_SHORTFALL" if self.count < plan.top_k else None},
                "filter_applied": True,
                "constraint_diagnostics": {"constraint_trace": [{"canonical_field": "industry", "executable": True}]},
                "index_compatibility": {"status": "compatible"},
                "latency_stages": {"total_retrieval_ms": 12.0},
            },
        )


def service_with(fake):
    service = object.__new__(WorkbenchService)
    service._c1_retriever = fake
    service._get_c1_retriever = MethodType(lambda self: fake, service)
    return service


class Gate7CWorkbenchTests(unittest.TestCase):
    def test_supported_contract_routes_to_c1_and_exposes_provenance(self):
        fake = _C1Fake(count=2)
        result = service_with(fake).structured_query("healthcare experts", {"hard_constraints": [{"canonical_field": "industry", "operator": "eq", "expected_value": "healthcare", "category": "categorical"}]}, requested_k=5)
        self.assertEqual(fake.calls, 1)
        self.assertEqual(result["profile"], "C1")
        self.assertEqual(result["answer_summary"]["contract_state"], "VALID")
        self.assertEqual(result["execution_context"]["planner"]["strategy"], "constraint_prefilter")
        self.assertEqual(result["metrics"]["shortfall"]["returned"], 2)
        self.assertEqual(result["raw_trace"]["provenance"]["index_compatibility"]["status"], "compatible")

    def test_unsupported_contract_never_calls_c1(self):
        fake = _C1Fake()
        result = service_with(fake).structured_query("recent experts", {"temporal_constraints": [{"operator": "after", "start": "2024-01-01"}]})
        self.assertEqual(fake.calls, 0)
        self.assertEqual(result["answer_summary"]["contract_state"], "UNSUPPORTED_CONSTRAINT")
        self.assertEqual(result["results"], [])

    def test_invalid_contract_is_distinct(self):
        fake = _C1Fake()
        result = service_with(fake).structured_query("bad", {"hard_constraints": [{"canonical_field": "industry", "operator": "eq", "expected_value": ["not-scalar"], "category": "categorical"}]})
        self.assertEqual(fake.calls, 0)
        self.assertEqual(result["answer_summary"]["contract_state"], "INVALID_CONTRACT")

    def test_structured_results_include_human_readable_constraint_evidence(self):
        fake = _C1Fake(count=1)
        item = ResultItem("expert-1", "expert", "Expert 1", "summary", {"years_experience": 24, "seniority": "principal", "industries": ["manufacturing"], "roles": ["technical_lead"], "locations": ["Portugal"]}, 1.0, ("elasticsearch_dense",), {"elasticsearch_dense_score": 1.0})
        fake.retrieve = lambda query, plan: RetrievalResult(items=(item,), plan_id=plan.plan_id, strategy=plan.strategy, latency_ms=1.0, provenance={"contract_state": "VALID", "requested_k": 5, "returned_k": 1, "shortfall": {"requested": 5, "returned": 1, "count": 4}, "constraint_diagnostics": {"constraint_trace": []}, "latency_stages": {"total_retrieval_ms": 1.0}})
        result = service_with(fake).structured_query("principal technical leads in manufacturing", {"hard_constraints": [{"canonical_field": "years_experience", "operator": "gte", "expected_value": 20, "category": "numeric"}, {"canonical_field": "seniority", "operator": "gte", "expected_value": "senior", "category": "seniority"}], "exclusions": [{"canonical_field": "industry", "operator": "eq", "expected_value": "healthcare", "category": "categorical"}], "semantic_query": "principal technical leads in manufacturing"}, requested_k=5)
        self.assertEqual(len(result["results"]), 1)
        evidence = result["results"][0]["constraint_evidence"]
        self.assertEqual([row["status"] for row in evidence], ["SATISFIED", "SATISFIED", "SATISFIED"])
        self.assertEqual(result["results"][0]["structured_facts"]["years_experience"], 24)


if __name__ == "__main__":
    unittest.main()
