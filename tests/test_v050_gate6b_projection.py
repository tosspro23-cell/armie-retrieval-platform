import unittest

from armie_retrieval.constraints import ElasticsearchConstraintCompiler
from armie_retrieval.contracts import Constraint, ConstraintCategory, ConstraintOperator, RetrievalContract
from armie_retrieval.datasets.v2 import V2DocumentProfileGenerator
from armie_retrieval.indexing.constraint_projection import (
    PROJECTION_IMPLEMENTATION_VERSION,
    project_profile,
    projection_mapping,
)


class Gate6BProjectionTests(unittest.TestCase):
    def test_supported_fields_are_canonical_and_rank_is_deterministic(self):
        profile = V2DocumentProfileGenerator(seed=7301).generate(17)
        projected = project_profile(profile)
        self.assertEqual(projected["years_experience"], profile.years_experience)
        self.assertEqual(projected["seniority"], profile.seniority)
        self.assertEqual(projected["industries"], profile.industries)
        self.assertEqual(projected["roles"], profile.roles)
        self.assertEqual(projected["locations"], profile.locations)
        self.assertEqual(projected["seniority_rank"], {"mid": 1, "senior": 2, "principal": 3}[profile.seniority])

    def test_mapping_contains_every_c1_supported_field(self):
        properties = projection_mapping()["mappings"]["properties"]
        for field in ("years_experience", "seniority", "seniority_rank", "industries", "roles", "locations"):
            self.assertIn(field, properties)

    def test_gate6b_projection_identity_is_explicit(self):
        self.assertEqual(PROJECTION_IMPLEMENTATION_VERSION, "constraint-projection-0.2-gate6b")

    def test_between_is_native_for_the_approved_numeric_scope(self):
        contract = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.BETWEEN, expected_value=(10, 15), category=ConstraintCategory.NUMERIC),))
        plan = ElasticsearchConstraintCompiler().compile(contract)[0]
        self.assertTrue(plan.executable)
        self.assertEqual(plan.dsl, {"range": {"years_experience": {"gte": 10, "lte": 15}}})


if __name__ == "__main__":
    unittest.main()
