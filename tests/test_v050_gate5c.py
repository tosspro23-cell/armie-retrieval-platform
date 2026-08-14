import gzip
import json
import unittest
from pathlib import Path


ROOT = Path("docs/v0.5.0/benchmark-extension-v1.1")


def lineage_valid(query):
    source = query["relevance_judgement_source"]
    return bool(query["base_query_id"]) and query["base_query_id"] == source["base_query_id"] and query["base_semantic_query"].lower() in query["execution_query_text"].lower()


class Gate5CSemanticRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text())
        cls.queries = json.loads((ROOT / "queries.json").read_text())
        cls.audit = json.loads((ROOT / "audit.json").read_text())

    def test_base_lineage_and_execution_text(self):
        self.assertEqual(len(self.queries), 46)
        for query in self.queries:
            self.assertTrue(lineage_valid(query))

    def test_changing_base_id_fails_lineage(self):
        query = dict(self.queries[0])
        query["base_query_id"] = "v2-q-does-not-exist"
        self.assertFalse(lineage_valid(query))

    def test_overlay_matches_contract_and_exclusions_are_separate(self):
        for query in self.queries:
            contract_fields = {**query["expected_contract"]["hard_constraints"], **query["expected_contract"]["exclusions"]}
            if query["category"] == "negative":
                self.assertFalse(query["expected_contract"]["hard_constraints"])
                self.assertTrue(query["expected_contract"]["exclusions"])
                self.assertEqual(query["constraint_overlay"]["industry"]["value"], [query["expected_contract"]["exclusions"]["industry"]["value"]])
            else:
                self.assertEqual(contract_fields, query["constraint_overlay"])

    def test_relevance_and_eligibility_are_independent(self):
        independent = False
        with gzip.open(ROOT / "judgements.jsonl.gz", "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["relevance_grade"] >= 2 and not row["eligible"]:
                    independent = True
                    break
        self.assertTrue(independent)

    def test_hard_negative_requires_relevance_and_violation(self):
        count = 0
        with gzip.open(ROOT / "judgements.jsonl.gz", "rt", encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["hard_negative_class"]:
                    self.assertGreaterEqual(row["relevance_grade"], 2)
                    self.assertIn("VIOLATED", row["constraint_status"].values())
                    count += 1
        self.assertEqual(count, self.manifest["hard_negative_candidate_count"])

    def test_scarcity_supply_is_recomputed(self):
        supply = self.audit["eligible_supply"]["per_query"]
        self.assertEqual(sum(value < 5 for value in supply.values()), self.manifest["scarcity_query_count"])
        self.assertEqual(sum(value >= 5 for value in supply.values()), self.manifest["supply_sufficient_query_count"])


if __name__ == "__main__":
    unittest.main()
