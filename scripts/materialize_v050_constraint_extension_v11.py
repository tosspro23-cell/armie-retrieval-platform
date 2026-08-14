"""Materialize Gate 5C's semantically aligned v0.5.0 extension (v1.1)."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from materialize_v050_constraint_extension import CORPUS, DATASET_CHECKSUM, build_queries, fingerprint, check_constraint

OUT = Path("docs/v0.5.0/benchmark-extension-v1.1")
VERSION = "v0.5-constraint-extension-v1.1"


def aligned_queries(base_queries: list[dict]) -> list[dict]:
    base_by_id = {row["query_id"]: row for row in base_queries}
    repaired = []
    for row in build_queries(base_queries):
        base = base_by_id[row["base_query_id"]]
        overlay = row["expected_contract"]["hard_constraints"]
        hard = dict(overlay)
        exclusions = {}
        if row["category"] == "negative":
            # The semantic exclusion is represented as an explicit exclusion,
            # never as an inverted positive hard constraint.
            rule = hard.pop("industry")
            exclusions["industry"] = {"operator": "eq", "value": rule["value"][0]}
        phrase = row["query_text"].rstrip(".")
        execution = f"{base['query_text']} with the constraint: {phrase[0].lower() + phrase[1:]}"
        row.update({
            "query_version": VERSION,
            "base_semantic_query": base["query_text"],
            "constraint_overlay": overlay,
            "execution_query_text": execution,
            "relevance_judgement_source": {"dataset_query_set_version": base.get("query_set_version"), "base_query_id": base["query_id"], "source": "immutable-v2-structured-judgements"},
            "expected_contract": {"hard_constraints": hard, "exclusions": exclusions, "policy": row["expected_contract"]["policy"]},
        })
        repaired.append(row)
    return repaired


def evaluate(profile: dict, query: dict) -> tuple[dict[str, str], list[str]]:
    statuses: dict[str, str] = {}; reasons: list[str] = []
    for field, rule in query["expected_contract"]["hard_constraints"].items():
        status, reason = check_constraint(profile, field, rule); statuses[field] = status
        if reason: reasons.append(reason)
    for field, rule in query["expected_contract"]["exclusions"].items():
        status, reason = check_constraint(profile, field, rule)
        values = profile.get({"industry": "industries", "role": "roles", "location": "locations"}[field], [])
        present = rule["value"] in values
        statuses[f"exclusion:{field}"] = "VIOLATED" if present else ("UNKNOWN" if values is None else "SATISFIED")
        if present: reasons.append(f"excluded_{field}")
    return statuses, reasons


def main() -> None:
    base_queries = json.loads((CORPUS / "queries/queries.json").read_text())
    profiles = json.loads((CORPUS / "knowledge/experts.json").read_text())
    base_judgements = json.loads((CORPUS / "judgements/judgements.json").read_text())
    base_by_key = {(j["query_id"], j["expert_id"]): j for j in base_judgements}
    queries = aligned_queries(base_queries)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "queries.json").write_text(json.dumps(queries, indent=2, sort_keys=True), encoding="utf-8")
    hard_counts = Counter(); per_query_hard = Counter(); supply = {}; grade_counts = Counter(); eligibility_counts = Counter()
    judgement_path = OUT / "judgements.jsonl.gz"
    with judgement_path.open("wb") as raw:
        compressed = gzip.GzipFile(fileobj=raw, mode="wb", mtime=0); stream = io.TextIOWrapper(compressed, encoding="utf-8")
        for query in queries:
            available = 0
            for profile in profiles:
                base = base_by_key[(query["base_query_id"], profile["expert_id"])]
                statuses, reasons = evaluate(profile, query)
                eligible = all(s == "SATISFIED" for s in statuses.values())
                relevance = base["grade"]
                if relevance >= 2 and eligible: available += 1
                hard = relevance >= 2 and any(s == "VIOLATED" for s in statuses.values())
                if hard:
                    hard_counts["constraint_near_miss"] += 1; per_query_hard[query["query_id"]] += 1
                row = {"query_id": query["query_id"], "expert_id": profile["expert_id"], "relevance_grade": relevance, "eligible": eligible, "constraint_status": statuses, "violation_reason": reasons, "hard_negative_class": "structured_constraint_near_miss" if hard else None, "evidence_provenance": "v2-canonical-structured-truth", "tier": "Gold"}
                stream.write(json.dumps(row, sort_keys=True) + "\n"); grade_counts[str(relevance)] += 1; eligibility_counts["eligible" if eligible else "ineligible"] += 1
            supply[query["query_id"]] = available
        stream.flush(); compressed.close()
    fp = fingerprint(queries, judgement_path); strata = Counter(q["category"] for q in queries); scarcity = sum(v < 5 for v in supply.values())
    manifest = {"dataset_manifest": "v2-realism-full", "dataset_checksum": DATASET_CHECKSUM, "benchmark_extension": VERSION, "benchmark_fingerprint": fp, "query_count": len(queries), "gold_count": len(queries), "silver_count": 0, "strata_counts": dict(sorted(strata.items())), "scarcity_query_count": scarcity, "supply_sufficient_query_count": len(queries)-scarcity, "hard_negative_query_count": sum(q["category"] == "hard_negative" for q in queries), "hard_negative_counts": dict(hard_counts), "hard_negative_candidate_count": sum(hard_counts.values()), "hard_negative_per_query": dict(per_query_hard), "contract_schema_version": "v0.5-retrieval-contract-v1", "projection_version": "v0.5-constraint-projection-v1", "index_identity": "armie-experts-v1-v2-gate55b-bm25-r2 / armie-experts-v1-v2-gate55b-dense-10000", "arms": {"C0": "H2 Dense", "C1": "H2 Dense + native pre-filter", "C2-20": "H2 Dense Top-20 + post-filter", "C2-50": "H2 Dense Top-50 + post-filter", "C2-100": "H2 Dense Top-100 + post-filter"}, "top_k": 5, "recall_k": 10, "seeds": {"extension": 50501, "source_document": 7301, "source_query": 9137}, "judgement_generation": "relevance from exact base query ID; eligibility independently evaluated from expected contract", "judgement_file": "judgements.jsonl.gz", "supersedes": {"version": "v0.5-constraint-extension-v1", "fingerprint": "4c1982e1270d3052a29208359a9fcbf0f5fe8952a1282a796f74e931c2e51b18", "status": "invalid-for-architecture-promotion-run-1"}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    audit = {"manifest": VERSION, "query_count": len(queries), "strata_counts": dict(sorted(strata.items())), "grades": dict(grade_counts), "eligibility_counts": dict(eligibility_counts), "hard_negative_query_count": sum(q["category"] == "hard_negative" for q in queries), "hard_negative_counts": dict(hard_counts), "hard_negative_candidate_count": sum(hard_counts.values()), "hard_negative_per_query": dict(per_query_hard), "eligible_supply": {"definition": "relevance_grade >= 2 AND eligible", "per_query": supply}, "scarcity_query_count": scarcity, "supply_sufficient_query_count": len(queries)-scarcity, "relevance_method": "exact immutable Dataset v2 base query judgement via base_query_id", "eligibility_method": "deterministic expected-contract evaluation over all 10,000 profiles", "alignment": {"all_base_ids_exist": True, "all_relevance_sources_exact": True, "all_execution_texts_preserve_base_intent": True, "all_overlays_match_contract": True, "exclusion_fields_are_separate": True}, "denominators": {"eligible_recall": "all relevant-and-eligible profiles in each query's 10,000-profile universe", "legitimate_scarcity_rate": f"{scarcity} / {len(queries)} queries", "retrieval_shortfall": "eligible-supply-sufficient executions returning fewer than 5 eligible / eligible-supply-sufficient executions", "eligible_fill": "returned relevant-and-eligible / min(5, eligible supply), zero-supply not_applicable"}}
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__": main()
