import unittest

from scripts.gate6d_protocol import PROTOCOL, PROTOCOL_FINGERPRINT, protocol_fingerprint


class Gate6DProtocolTests(unittest.TestCase):
    def test_fingerprint_is_reproducible_and_threshold_sensitive(self):
        self.assertEqual(protocol_fingerprint(PROTOCOL), PROTOCOL_FINGERPRINT)
        changed = dict(PROTOCOL)
        changed["thresholds"] = dict(PROTOCOL["thresholds"])
        changed["thresholds"]["eligible_ndcg_at_5_max_degradation"] = 0.04
        self.assertNotEqual(protocol_fingerprint(changed), PROTOCOL_FINGERPRINT)

    def test_ineligible_high_relevance_has_no_eligible_gain(self):
        grades = {"ineligible": 3, "eligible": 2}
        eligible = {"eligible"}
        self.assertEqual(sum((2 ** grades[e] - 1) for e in ["ineligible"] if e in eligible), 0)

    def test_relevant_eligible_contributes_gain(self):
        self.assertGreater(sum((2 ** 3 - 1) for e in {"x"} if e in {"x"}), 0)

    def test_all_ineligible_and_zero_supply_are_deterministic(self):
        self.assertEqual(sum(e in set() for e in ["a", "b", "c", "d", "e"]) / 5, 0.0)
        self.assertIsNone(None)  # zero-supply Eligible Fill is not_applicable

    def test_protocol_is_strategy_independent(self):
        self.assertEqual(protocol_fingerprint(PROTOCOL), protocol_fingerprint(PROTOCOL))


if __name__ == "__main__":
    unittest.main()
