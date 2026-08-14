import unittest
from datetime import date

from armie_retrieval.constraints import ConstraintPolarity, ElasticsearchConstraintCompiler
from armie_retrieval.contracts import Constraint, ConstraintCategory, ConstraintOperator, RetrievalContract, UnsupportedConstraint, ValidationState
from armie_retrieval.datasets.v2 import V2DocumentProfileGenerator
from armie_retrieval.indexing.constraint_projection import PROJECTION_SCHEMA_VERSION, project_profile, projection_mapping


class ProjectionCompilerTests(unittest.TestCase):
    def test_projection_preserves_nested_boundaries_and_normalizes_relationship(self):
        projected = project_profile(V2DocumentProfileGenerator(seed=7301).generate(0))
        self.assertEqual(projected["relationships"][0]["predicate"], "worked_at")
        self.assertIn("employments", projected)
        self.assertEqual(projection_mapping()["mappings"]["properties"]["employments"]["type"], "nested")
        self.assertEqual(PROJECTION_SCHEMA_VERSION, "armie-v0.5-constraint-projection-v1")

    def test_allowlisted_profile_constraints_compile_deterministically(self):
        contract = RetrievalContract(semantic_query="search", hard_constraints=(
            Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=["Energy", "Banking"], category=ConstraintCategory.CATEGORICAL),
            Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC),
        ))
        first = ElasticsearchConstraintCompiler().compile(contract)
        second = ElasticsearchConstraintCompiler().compile(contract.model_copy(deep=True))
        self.assertEqual(first, second)
        self.assertEqual(first[0].dsl, {"terms": {"industries": ["Banking", "Energy"]}})
        self.assertEqual(first[1].dsl, {"range": {"years_experience": {"gte": 20}}})

    def test_unsupported_and_unapproved_semantics_are_retained(self):
        unsupported = RetrievalContract(semantic_query="x", unsupported_constraints=(UnsupportedConstraint(expression="relationship worked_at Shell", reason="nested scope not approved"),))
        plans = ElasticsearchConstraintCompiler().compile(unsupported)
        self.assertFalse(plans[0].executable)
        self.assertEqual(plans[0].reason, ValidationState.UNSUPPORTED_CONSTRAINT.value)

    def test_no_arbitrary_field_or_dsl_injection(self):
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="__proto__", operator=ConstraintOperator.EQ, expected_value="x", category=ConstraintCategory.CATEGORICAL),))
        plan = ElasticsearchConstraintCompiler().compile(contract)[0]
        self.assertFalse(plan.executable)
        self.assertIsNone(plan.dsl)

    def test_seniority_enum_and_rank_semantics(self):
        compiler = ElasticsearchConstraintCompiler()
        for op in (ConstraintOperator.EQ, ConstraintOperator.IN, ConstraintOperator.NOT_IN):
            value = "senior" if op is ConstraintOperator.EQ else ["mid", "principal"]
            plan = compiler.compile(RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="seniority", operator=op, expected_value=value, category=ConstraintCategory.SENIORITY),)))[0]
            self.assertTrue(plan.executable)
            self.assertIn("seniority", str(plan.dsl))
        for op, key in ((ConstraintOperator.GTE, "gte"), (ConstraintOperator.GT, "gt"), (ConstraintOperator.LTE, "lte"), (ConstraintOperator.LT, "lt")):
            plan = compiler.compile(RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="seniority", operator=op, expected_value="senior", category=ConstraintCategory.SENIORITY),)))[0]
            self.assertEqual(plan.dsl, {"range": {"seniority_rank": {key: 2}}})
        unknown = compiler.compile(RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="seniority", operator=ConstraintOperator.EQ, expected_value="executive", category=ConstraintCategory.SENIORITY),)))[0]
        self.assertFalse(unknown.executable)

    def test_exclusion_is_negative_polarity(self):
        plan = ElasticsearchConstraintCompiler().compile(RetrievalContract(semantic_query="x", exclusions=(Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Banking", category=ConstraintCategory.CATEGORICAL),)))[0]
        self.assertEqual(plan.polarity, ConstraintPolarity.EXCLUDED)
        self.assertEqual(plan.dsl, {"bool": {"must_not": [{"term": {"industries": "Banking"}}]}})

    def test_set_like_dsl_is_canonical(self):
        compiler = ElasticsearchConstraintCompiler()
        a = compiler.compile(RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=["Energy", "Banking"], category=ConstraintCategory.CATEGORICAL),)))[0]
        b = compiler.compile(RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=["Banking", "Energy"], category=ConstraintCategory.CATEGORICAL),)))[0]
        self.assertEqual(a.value, b.value)
        self.assertEqual(a.dsl, b.dsl)


if __name__ == "__main__":
    unittest.main()
