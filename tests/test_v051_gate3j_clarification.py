import unittest

from armie_retrieval.interpretation import (
    CandidateInterpretation, ClarificationItem, ClarificationResolution,
    ClarificationStatus, ClarificationType, InterpretationState, apply_resolution,
    confirm, start_session, validate_contract,
)


def item(kind=ClarificationType.REQUIREMENT_STRENGTH, *, depends=()):
    return ClarificationItem("c1", "q1", "senior experts", "full request", "AMBIGUOUS", kind, ("REQUIRED", "PREFERRED", "CONTEXT_ONLY"), "How should this be treated?", ("REQUIRED", "PREFERRED", "CONTEXT_ONLY"), depends_on=depends)


class Gate3JTests(unittest.TestCase):
    def base(self):
        return CandidateInterpretation("q1", "senior experts", "senior experts")

    def test_no_clarification_fast_path_still_requires_confirmation(self):
        s = start_session(self.base())
        self.assertEqual(s.interpretation.interpretation_state, InterpretationState.INTERPRETATION_COMPLETE)
        with self.assertRaises(ValueError): validate_contract(s)
        self.assertEqual(validate_contract(confirm(s)).interpretation.interpretation_state, InterpretationState.VALIDATED_CONTRACT)

    def test_blocking_clarification_cannot_confirm(self):
        s = start_session(self.base(), (item(),))
        self.assertEqual(s.interpretation.interpretation_state, InterpretationState.NEEDS_CLARIFICATION)
        with self.assertRaises(ValueError): confirm(s)

    def test_resolution_is_deterministic_and_provenanced(self):
        s = apply_resolution(start_session(self.base(), (item(),)), ClarificationResolution("c1", "PREFERRED"))
        self.assertEqual(s.clarifications[0].status, ClarificationStatus.RESOLVED)
        self.assertEqual(s.interpretation.interpretation_state, InterpretationState.INTERPRETATION_COMPLETE)
        self.assertEqual(s.interpretation.evidence[-1]["source"], "user")

    def test_unknown_and_inconsistent_resolution_rejected(self):
        s = start_session(self.base(), (item(),))
        with self.assertRaises(ValueError): apply_resolution(s, ClarificationResolution("missing", "PREFERRED"))
        s = apply_resolution(s, ClarificationResolution("c1", "PREFERRED"))
        with self.assertRaises(ValueError): apply_resolution(s, ClarificationResolution("c1", "REQUIRED"))
        self.assertEqual(apply_resolution(s, ClarificationResolution("c1", "REQUIRED", sequence=2), edit=True).resolutions[-1].sequence, 2)

    def test_remove_invalidates_dependents(self):
        parent = ClarificationItem("c1", "q1", "senior", "full", "AMBIGUOUS", ClarificationType.REQUIREMENT_STRENGTH, ("CONTEXT_ONLY", "REMOVE_FROM_CONSTRAINT_INTERPRETATION"), "How?")
        child = ClarificationItem("c2", "q1", "years", "full", "AMBIGUOUS", ClarificationType.NUMERIC_INTENT, ("REMOVE_FROM_CONSTRAINT_INTERPRETATION",), "How?", depends_on=("c1",))
        s = apply_resolution(start_session(self.base(), (parent, child)), ClarificationResolution("c1", "REMOVE_FROM_CONSTRAINT_INTERPRETATION"))
        self.assertEqual(s.clarifications[0].status, ClarificationStatus.CANCELLED)
        self.assertEqual(s.clarifications[1].status, ClarificationStatus.CANCELLED)

    def test_unsupported_resolution_does_not_create_executable_constraint(self):
        unsupported = ClarificationItem("c1", "q1", "worked at Acme", "full", "UNSUPPORTED", ClarificationType.UNSUPPORTED_INTENT, ("ACKNOWLEDGE_UNSUPPORTED",), "How?",)
        s = apply_resolution(start_session(self.base(), (unsupported,)), ClarificationResolution("c1", "ACKNOWLEDGE_UNSUPPORTED"))
        self.assertFalse(s.interpretation.constraints)


if __name__ == "__main__": unittest.main()
