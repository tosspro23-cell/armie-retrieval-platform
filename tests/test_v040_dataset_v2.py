"""Gate 5.5A Dataset v2 design and quality-gate tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from armie_retrieval.datasets.generator import build_dataset, load_dataset
from armie_retrieval.datasets.v2 import (
    DOCUMENT_SURFACES,
    QUERY_SURFACES,
    V2DocumentProfileGenerator,
    V2JudgementBuilder,
    V2QueryGenerator,
    audit_v2_pilot,
    build_v2_pilot,
    pipeline_boundaries,
    validate_query_contracts,
)
from armie_retrieval.relevance.contracts import QueryCategory, generate_benchmark_queries


class DatasetV2Tests(unittest.TestCase):
    def test_v1_remains_immutable_and_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            a = build_dataset(first, size=25, seed=42)
            b = build_dataset(second, size=25, seed=42)
            self.assertEqual(a.checksum, b.checksum)
            self.assertEqual(a.dataset_id, "expert-discovery")
            self.assertEqual(a.schema_version, "expert-profile-v1")
            self.assertEqual([p.model_dump(mode="json") for p in load_dataset(first)], [p.model_dump(mode="json") for p in load_dataset(second)])

    def test_v2_is_deterministic_and_seeded_separately(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second, tempfile.TemporaryDirectory() as different:
            a = build_v2_pilot(first, size=500, seed=7301, query_seed=9137)
            b = build_v2_pilot(second, size=500, seed=7301, query_seed=9137)
            c = build_v2_pilot(different, size=500, seed=7302, query_seed=9138)
            self.assertEqual(a.checksum, b.checksum)
            self.assertNotEqual(a.checksum, c.checksum)
            self.assertNotEqual(a.document_seed, a.query_seed)
            self.assertEqual(a.dataset_id, "expert-discovery-v2-realism")

    def test_pipeline_separation_is_explicit(self) -> None:
        boundaries = pipeline_boundaries(7301, 9137)
        self.assertNotEqual(boundaries["document_pipeline"]["seed"], boundaries["query_pipeline"]["seed"])
        self.assertEqual(boundaries["judgement_pipeline"]["forbidden_inputs"], ["search_document", "query_text", "retrieval_results"])
        self.assertEqual(set(boundaries["shared_inputs"]), {"canonical ontology IDs"})
        document_phrases = {phrase for phrases in DOCUMENT_SURFACES.values() for phrase in phrases}
        query_phrases = {phrase for phrases in QUERY_SURFACES.values() for phrase in phrases}
        self.assertTrue(document_phrases.isdisjoint(query_phrases))

    def test_relationship_and_temporal_integrity(self) -> None:
        profiles = [V2DocumentProfileGenerator(seed=7301).generate(i) for i in range(40)]
        for profile in profiles:
            predicates = {edge.predicate for edge in profile.relationships}
            self.assertIn("works_at", predicates)
            self.assertIn("delivered_for", predicates)
            self.assertIn("has_project", predicates)
            employers = {edge.object_id for edge in profile.relationships if edge.predicate == "works_at"}
            clients = {edge.object_id for edge in profile.relationships if edge.predicate == "delivered_for"}
            self.assertTrue(employers.isdisjoint(clients))
            for employment in profile.employers:
                if employment.end_date:
                    self.assertGreaterEqual(employment.end_date, employment.start_date)
            for project in profile.projects:
                self.assertGreater(project.end_date, project.start_date)
                self.assertTrue(any(edge.object_id == project.client_id and edge.predicate == "delivered_for" for edge in profile.relationships))
            evidence_ids = {e.evidence_id for e in profile.evidence}
            self.assertTrue(all(eid in evidence_ids for edge in profile.relationships for eid in edge.evidence_ids))

    def test_query_taxonomy_and_canonical_judgements(self) -> None:
        profiles = [V2DocumentProfileGenerator(seed=7301).generate(i) for i in range(80)]
        queries = V2QueryGenerator(seed=9137).generate(40)
        self.assertEqual({q.category for q in queries}, set(QueryCategory))
        judgements = V2JudgementBuilder().build(queries, profiles)
        self.assertEqual(len(judgements), len(queries) * len(profiles))
        self.assertTrue(any(j.grade == 3 for j in judgements))
        self.assertTrue(any(j.grade == 2 for j in judgements))
        self.assertTrue(any(j.grade == 1 for j in judgements))
        self.assertTrue(any(j.grade == 0 for j in judgements))
        self.assertTrue(any(j.grade == 0 for j, q in zip(judgements, [queries[i // len(profiles)] for i in range(len(judgements))]) if q.category is QueryCategory.hard_negative))
        self.assertTrue(all(j.review_status in {"draft_gold_structured_audit", "draft_silver_rule_assisted"} for j in judgements))

    def test_pilot_quality_audit_and_v1_overlap_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as v2_root, tempfile.TemporaryDirectory() as v1_root:
            build_v2_pilot(v2_root, size=500, seed=7301, query_seed=9137)
            build_dataset(v1_root, size=500, seed=42)
            v1_queries = generate_benchmark_queries(targets={category: 4 for category in QueryCategory})
            audit = audit_v2_pilot(v2_root, v1_profiles=load_dataset(v1_root), v1_queries=v1_queries)
            self.assertLess(audit["duplicates"]["normalized_summary_duplicate_rate"], 0.05)
            self.assertEqual(audit["temporal"]["invalid_records"], 0)
            self.assertEqual(audit["manual_inspection"]["profiles"].__len__(), 20)
            self.assertEqual(audit["manual_inspection"]["queries"].__len__(), 20)
            self.assertEqual(audit["manual_inspection"]["grade_coverage"], [0, 1, 2, 3])
            self.assertTrue(audit["v1_comparison"]["v2_lower_overlap"])
            self.assertEqual(audit["counts"]["queries"], 40)

    def test_refinement_role_narrative_and_query_semantics(self) -> None:
        profiles = [V2DocumentProfileGenerator(seed=7301).generate(i) for i in range(750)]
        queries = V2QueryGenerator(seed=9137).generate(40)
        self.assertGreaterEqual(len({p.roles[0] for p in profiles}), 10)
        self.assertGreaterEqual(len({p.seniority for p in profiles}), 3)
        self.assertGreaterEqual(len({p.narrative_style for p in profiles}), 8)
        self.assertLessEqual(max(sum(p.narrative_style == s for p in profiles) for s in {p.narrative_style for p in profiles}), 100)
        for q in queries:
            if q.category is QueryCategory.organization:
                self.assertTrue(q.organization_required and q.relationship_required)
            if q.category is QueryCategory.seniority_role:
                self.assertTrue(q.role_required and q.seniority_required)
            if q.category is QueryCategory.skill_industry:
                self.assertTrue(q.canonical_required and q.industry_required)
            if q.category is QueryCategory.delivery_project:
                self.assertTrue(q.evidence_required or q.relationship_required)
            if q.category is QueryCategory.temporal:
                self.assertIsNotNone(q.temporal_start); self.assertIsNotNone(q.temporal_end)
            if q.category is QueryCategory.negative_constraint:
                self.assertTrue(q.canonical_prohibited)
        self.assertGreaterEqual(sum(q.semantic_bucket == "low_overlap" for q in queries), 1)
        self.assertEqual({q.hard_negative_type for q in queries if q.category is QueryCategory.hard_negative}, {"wrong_relationship", "advisory_only", "outside_window", "missing_skill"})

    def test_structured_grade_contract(self) -> None:
        profiles = [V2DocumentProfileGenerator(seed=7301).generate(i) for i in range(80)]
        queries = V2QueryGenerator(seed=9137).generate(40)
        judgements = V2JudgementBuilder().build(queries, profiles)
        by_query = {q.query_id: q for q in queries}
        for judgement in judgements:
            query = by_query[judgement.query_id]
            if judgement.grade == 3:
                self.assertFalse(judgement.missing_requirements)
                self.assertFalse(judgement.violated_concepts)
            if query.category is QueryCategory.hard_negative and judgement.grade == 1:
                self.assertTrue(judgement.missing_requirements or judgement.missing_concepts)

    def test_language_contract_and_hard_negative_denominators(self) -> None:
        queries = V2QueryGenerator(seed=9137).generate(40)
        validation = validate_query_contracts(queries)
        self.assertTrue(validation["valid"], validation["rows"])
        multi = [q for q in queries if q.category is QueryCategory.multi_constraint]
        self.assertEqual(len(multi), 4)
        for query in multi:
            self.assertIn("technical_leadership", query.canonical_required)
            self.assertNotIn("technical_leadership", query.canonical_optional)
            self.assertIn("technical leadership required", query.query_text)
            self.assertTrue(query.industry_required)
        with tempfile.TemporaryDirectory() as root:
            build_v2_pilot(root, size=500, seed=7301, query_seed=9137)
            audit = audit_v2_pilot(root)
        metrics = audit["hard_negatives"]
        self.assertIn("legacy_density", metrics)
        self.assertIn("negative_judgement_rate", metrics)
        self.assertIn("hard_negative_judgement_rate", metrics)
        self.assertIn("easy_negative_rate", metrics)
        self.assertEqual(metrics["hard_negative_query_count"], 4)
        self.assertEqual(set(metrics["hard_negative_type_distribution"]), {"wrong_relationship", "advisory_only", "outside_window", "missing_skill"})
        self.assertEqual(metrics["negative_judgement_rate"] + 0, round((audit["grades"].get("0", audit["grades"].get(0, 0))) / audit["counts"]["judgements"], 6))


if __name__ == "__main__":
    unittest.main()
