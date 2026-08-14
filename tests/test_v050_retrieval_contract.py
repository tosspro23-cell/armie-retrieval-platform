import unittest
from datetime import date

from armie_retrieval.contracts import (
    CandidateConstraintResult,
    Constraint,
    ConstraintCategory,
    ConstraintOperator,
    ConstraintPolicy,
    ConstraintState,
    ConstraintStrength,
    RelationshipConstraint,
    RelationshipType,
    RetrievalContract,
    TemporalConstraint,
    TemporalOperator,
    UnsupportedConstraint,
    ValidationState,
    validate_contract,
)


class RetrievalContractTests(unittest.TestCase):
    def test_valid_constraint_shapes_and_contract_identity(self):
        contract = RetrievalContract(
            semantic_query="energy engineer",
            hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC),),
            soft_preferences=(Constraint(canonical_field="location", operator=ConstraintOperator.EQ, expected_value="Europe", category=ConstraintCategory.CATEGORICAL, strength=ConstraintStrength.SOFT),),
        )
        self.assertTrue(contract.contract_id.startswith("contract-"))
        self.assertEqual(validate_contract(contract).state, ValidationState.VALID)
        self.assertEqual(contract.model_copy(deep=True).contract_id, contract.contract_id)

    def test_negative_temporal_and_relationship_types(self):
        contract = RetrievalContract(
            semantic_query="energy delivery",
            exclusions=(Constraint(canonical_field="prohibited_capability", operator=ConstraintOperator.EQ, expected_value="advisory_only", category=ConstraintCategory.NEGATIVE),),
            temporal_constraints=(TemporalConstraint(operator=TemporalOperator.BETWEEN, start=date(2022, 1, 1), end=date(2025, 12, 31)),),
            relationship_constraints=(RelationshipConstraint(relation=RelationshipType.DELIVERED_FOR, object="client-1"),),
        )
        self.assertTrue(validate_contract(contract).valid)

    def test_operator_validation(self):
        self.assertTrue(validate_contract(RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.BETWEEN, expected_value=(10, 20), category=ConstraintCategory.NUMERIC),))).valid)
        with self.assertRaises(ValueError):
            Constraint(canonical_field="years_experience", operator=ConstraintOperator.BETWEEN, expected_value=(20,), category=ConstraintCategory.NUMERIC)
        with self.assertRaises(ValueError):
            Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=[], category=ConstraintCategory.CATEGORICAL)
        mismatch = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="years_experience", operator=ConstraintOperator.EQ, expected_value="twenty", category=ConstraintCategory.NUMERIC),))
        self.assertEqual(validate_contract(mismatch).state, ValidationState.TYPE_MISMATCH)

    def test_strict_policy_and_soft_boundary(self):
        policy = ConstraintPolicy()
        self.assertEqual(policy.mode, "strict")
        self.assertEqual(policy.unknown_hard_constraint, "exclude")
        self.assertFalse(policy.silent_relaxation)
        with self.assertRaises(ValueError):
            RetrievalContract(semantic_query="x", hard_constraints=(Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Energy", category=ConstraintCategory.CATEGORICAL, strength=ConstraintStrength.SOFT),))
        with self.assertRaises(ValueError):
            Constraint(canonical_field="prohibited_capability", operator=ConstraintOperator.EQ, expected_value="x", category=ConstraintCategory.NEGATIVE, strength=ConstraintStrength.SOFT)

    def test_three_valued_candidate_state_is_distinct(self):
        self.assertEqual({CandidateConstraintResult(constraint_id="c", status=s).status for s in ConstraintState}, set(ConstraintState))
        self.assertNotEqual(ConstraintState.UNKNOWN, ConstraintState.VIOLATED)
        self.assertNotEqual(ConstraintState.UNKNOWN, ConstraintState.SATISFIED)

    def test_contradictions_are_bounded_and_deterministic(self):
        cases = [
            (Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC), Constraint(canonical_field="years_experience", operator=ConstraintOperator.LT, expected_value=10, category=ConstraintCategory.NUMERIC)),
            (Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Banking", category=ConstraintCategory.CATEGORICAL), Constraint(canonical_field="industry", operator=ConstraintOperator.NEQ, expected_value="Banking", category=ConstraintCategory.CATEGORICAL)),
            (Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=["Banking"], category=ConstraintCategory.CATEGORICAL), Constraint(canonical_field="industry", operator=ConstraintOperator.NOT_IN, expected_value=["Banking"], category=ConstraintCategory.CATEGORICAL)),
        ]
        for first, second in cases:
            a = validate_contract(RetrievalContract(semantic_query="x", hard_constraints=(first, second)))
            b = validate_contract(RetrievalContract(semantic_query="x", hard_constraints=(second, first)))
            self.assertEqual(a.state, ValidationState.CONTRADICTION)
            self.assertEqual(a.state, b.state)

    def test_unsupported_is_not_unknown_or_violation(self):
        contract = RetrievalContract(semantic_query="x", unsupported_constraints=(UnsupportedConstraint(expression="exceptional executive presence", reason="no canonical evidence field"),))
        result = validate_contract(contract)
        self.assertEqual(result.state, ValidationState.UNSUPPORTED_CONSTRAINT)
        self.assertEqual(ConstraintState.UNKNOWN.value, "UNKNOWN")
        self.assertNotEqual(result.state, ValidationState.VALID)
        self.assertNotEqual(result.state, ValidationState.CONTRADICTION)

    def test_temporal_bounds_are_semantically_required(self):
        with self.assertRaises(ValueError):
            TemporalConstraint(operator=TemporalOperator.AFTER)
        with self.assertRaises(ValueError):
            TemporalConstraint(operator=TemporalOperator.BEFORE)
        with self.assertRaises(ValueError):
            TemporalConstraint(operator=TemporalOperator.BETWEEN, start=date(2024, 1, 1))

    def test_numeric_equal_bounds_are_explicit_and_safe(self):
        valid = RetrievalContract(semantic_query="x", hard_constraints=(
            Constraint(canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.NUMERIC),
            Constraint(canonical_field="years_experience", operator=ConstraintOperator.LTE, expected_value=20, category=ConstraintCategory.NUMERIC),
        ))
        self.assertEqual(validate_contract(valid).state, ValidationState.VALID)
        for lower, upper in ((ConstraintOperator.GTE, ConstraintOperator.LT), (ConstraintOperator.GT, ConstraintOperator.LTE), (ConstraintOperator.GT, ConstraintOperator.LT)):
            contract = RetrievalContract(semantic_query="x", hard_constraints=(
                Constraint(canonical_field="years_experience", operator=lower, expected_value=20, category=ConstraintCategory.NUMERIC),
                Constraint(canonical_field="years_experience", operator=upper, expected_value=20, category=ConstraintCategory.NUMERIC),
            ))
            self.assertEqual(validate_contract(contract).state, ValidationState.CONTRADICTION)

    def test_set_like_identity_is_order_independent(self):
        first = Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=["Energy", "Banking"], category=ConstraintCategory.CATEGORICAL)
        second = Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=["Banking", "Energy"], category=ConstraintCategory.CATEGORICAL)
        third = Constraint(canonical_field="industry", operator=ConstraintOperator.IN, expected_value=frozenset({"Banking", "Energy"}), category=ConstraintCategory.CATEGORICAL)
        self.assertEqual(first.constraint_id, second.constraint_id)
        self.assertEqual(first.constraint_id, third.constraint_id)

    def test_registry_category_is_semantic_authority(self):
        mismatch = RetrievalContract(semantic_query="x", hard_constraints=(Constraint(
            canonical_field="years_experience", operator=ConstraintOperator.GTE, expected_value=20, category=ConstraintCategory.CATEGORICAL,
        ),))
        result = validate_contract(mismatch)
        self.assertEqual(result.state, ValidationState.INVALID_CONTRACT)
        self.assertTrue(any(issue.reason_code == "field_category_mismatch" for issue in result.issues))

    def test_serialization_preserves_semantics_and_ordering(self):
        c = Constraint(canonical_field="industry", operator=ConstraintOperator.EQ, expected_value="Energy", category=ConstraintCategory.CATEGORICAL)
        contract = RetrievalContract(semantic_query="energy", hard_constraints=(c,))
        restored = RetrievalContract.model_validate(contract.model_dump(mode="json"))
        self.assertEqual(restored, contract)


if __name__ == "__main__":
    unittest.main()
