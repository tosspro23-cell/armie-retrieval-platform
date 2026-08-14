"""Materialize the versioned v0.5 constraint benchmark extension.

This is an offline asset builder. It reads the immutable Dataset v2 full
corpus, writes a separate query/judgement extension, and never changes the
canonical corpus or the v0.4 benchmark.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


CORPUS = Path("/tmp/armie-v040-dataset-v2-full")
OUT = Path("docs/v0.5.0/benchmark-extension-v1")
DATASET_CHECKSUM = "514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc"
VERSION = "v0.5-constraint-extension-v1"
SEED = 50501


def fingerprint(queries: list[dict], judgements_path: Path) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(queries, sort_keys=True, separators=(",", ":")).encode())
    with judgements_path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build_queries(base: list[dict]) -> list[dict]:
    # Relevance remains anchored to existing structured judgements for the
    # semantic concept; eligibility is computed independently below.
    bases = [base[i] for i in (0, 10, 20, 30)]
    specs = []
    templates = [
        ("numeric", "Find candidates with at least 20 years of experience.", {"years_experience": {"operator": "gte", "value": 20}}),
        ("numeric", "Find candidates with 10 to 15 years of experience.", {"years_experience": {"operator": "between", "value": [10, 15]}}),
        ("numeric_boundary", "Find candidates at the 20-year experience boundary.", {"years_experience": {"operator": "gte", "value": 20}}),
        ("numeric_boundary", "Find candidates with exactly 5 years of experience.", {"years_experience": {"operator": "eq", "value": 5}}),
        ("industry", "Find candidates in manufacturing.", {"industry": {"operator": "eq", "value": "manufacturing"}}),
        ("industry", "Find candidates in financial services.", {"industry": {"operator": "eq", "value": "financial services"}}),
        ("role", "Find Data Scientists.", {"role": {"operator": "eq", "value": "Data Scientist"}}),
        ("role", "Find Search / Retrieval Engineers.", {"role": {"operator": "eq", "value": "Search / Retrieval Engineer"}}),
        ("location", "Find candidates based in Portugal.", {"location": {"operator": "eq", "value": "Portugal"}}),
        ("location", "Find candidates based in the United Kingdom.", {"location": {"operator": "eq", "value": "United Kingdom"}}),
        ("seniority", "Find senior candidates.", {"seniority": {"operator": "gte", "value": "senior"}}),
        ("seniority", "Find principal-only candidates.", {"seniority": {"operator": "eq", "value": "principal"}}),
        ("negative", "Find candidates excluding manufacturing.", {"industry": {"operator": "not_in", "value": ["manufacturing"]}}),
        ("negative", "Find candidates excluding financial services.", {"industry": {"operator": "not_in", "value": ["financial services"]}}),
        ("multi_constraint", "Find manufacturing candidates with at least 20 years of experience.", {"industry": {"operator": "eq", "value": "manufacturing"}, "years_experience": {"operator": "gte", "value": 20}}),
        ("multi_constraint", "Find financial-services candidates with at least 20 years of experience.", {"industry": {"operator": "eq", "value": "financial services"}, "years_experience": {"operator": "gte", "value": 20}}),
        ("multi_constraint_3plus", "Find manufacturing principal candidates with at least 20 years of experience.", {"industry": {"operator": "eq", "value": "manufacturing"}, "years_experience": {"operator": "gte", "value": 20}, "seniority": {"operator": "eq", "value": "principal"}}),
        ("multi_constraint_3plus", "Find senior Search / Retrieval Engineers in Portugal with at least 20 years of experience.", {"role": {"operator": "eq", "value": "Search / Retrieval Engineer"}, "location": {"operator": "eq", "value": "Portugal"}, "years_experience": {"operator": "gte", "value": 20}, "seniority": {"operator": "gte", "value": "senior"}}),
        ("selective", "Find principal Data Scientists in manufacturing with at least 30 years of experience.", {"role": {"operator": "eq", "value": "Data Scientist"}, "industry": {"operator": "eq", "value": "manufacturing"}, "years_experience": {"operator": "gte", "value": 30}, "seniority": {"operator": "eq", "value": "principal"}}),
        ("selective", "Find principal Search / Retrieval Engineers in Portugal with at least 30 years of experience.", {"role": {"operator": "eq", "value": "Search / Retrieval Engineer"}, "location": {"operator": "eq", "value": "Portugal"}, "years_experience": {"operator": "gte", "value": 30}, "seniority": {"operator": "eq", "value": "principal"}}),
        ("hard_negative", "Find manufacturing candidates with at least 20 years and principal seniority.", {"industry": {"operator": "eq", "value": "manufacturing"}, "years_experience": {"operator": "gte", "value": 20}, "seniority": {"operator": "eq", "value": "principal"}}),
        ("hard_negative", "Find senior Search / Retrieval Engineers, excluding financial services.", {"role": {"operator": "eq", "value": "Search / Retrieval Engineer"}, "seniority": {"operator": "gte", "value": "senior"}, "industry": {"operator": "not_in", "value": ["financial services"]}}),
        ("unknown", "Find candidates with a verifiable years-of-experience value of at least 20.", {"years_experience": {"operator": "gte", "value": 20, "unknown_if_missing": True}}),
    ]
    # Two deterministic rounds provide 44 cases with broad, balanced strata.
    for round_no in range(2):
        for offset, (category, text, constraints) in enumerate(templates):
            base_row = bases[(offset + round_no) % len(bases)]
            specs.append({
                "query_id": f"v05-cq-{len(specs)+1:03d}",
                "query_text": text,
                "category": category,
                "base_query_id": base_row["query_id"],
                "semantic_required": list(base_row.get("canonical_required", [])),
                "expected_contract": {"hard_constraints": constraints, "exclusions": [], "policy": {"mode": "strict", "unknown_hard_constraint": "exclude", "silent_relaxation": False}},
                "supported": True,
                "support_note": "missing candidate value is evaluated as UNKNOWN" if category == "unknown" else "deterministic contract field",
                "gold_tier": "Gold",
                "query_version": VERSION,
            })
    return specs


def values(profile: dict, field: str):
    mapping = {"industry": profile.get("industries", []), "role": profile.get("roles", []), "location": profile.get("locations", []), "seniority": [profile.get("seniority")], "years_experience": profile.get("years_experience")}
    return mapping[field]


def check_constraint(profile: dict, field: str, rule: dict) -> tuple[str, str]:
    actual = values(profile, field)
    if actual is None or actual == [] or (rule.get("unknown_if_missing") and actual is None):
        return "UNKNOWN", "missing_observed_value"
    op, expected = rule["operator"], rule["value"]
    if field in {"industry", "role", "location"}:
        hit = expected in actual if op == "eq" else any(v in actual for v in expected)
        ok = hit if op == "eq" else (not hit)
    elif field == "seniority":
        rank = {"mid": 1, "senior": 2, "principal": 3}
        a = rank.get(actual[0], 0); e = rank.get(expected, 0)
        ok = a == e if op == "eq" else a >= e
    else:
        a = actual
        if op == "eq":
            ok = a == expected
        elif op == "gte":
            ok = a >= expected
        elif op == "between":
            ok = expected[0] <= a <= expected[1]
        else:
            raise ValueError(f"unsupported numeric operator: {op}")
    return ("SATISFIED" if ok else "VIOLATED"), ("" if ok else f"{field}_{op}_failed")


def main() -> None:
    base_queries = json.loads((CORPUS / "queries/queries.json").read_text())
    profiles = json.loads((CORPUS / "knowledge/experts.json").read_text())
    base_judgements = json.loads((CORPUS / "judgements/judgements.json").read_text())
    base_by_key = {(j["query_id"], j["expert_id"]): j for j in base_judgements}
    queries = build_queries(base_queries)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "queries.json").write_text(json.dumps(queries, indent=2, sort_keys=True), encoding="utf-8")
    grades = Counter(); statuses = Counter(); hard_negative = Counter(); supply = Counter(); relevant_eligible = Counter()
    judgement_path = OUT / "judgements.jsonl.gz"
    with judgement_path.open("wb") as raw:
        compressed = gzip.GzipFile(fileobj=raw, mode="wb", mtime=0)
        stream = io.TextIOWrapper(compressed, encoding="utf-8")
        for query in queries:
            available = 0
            for profile in profiles:
                base = base_by_key[(query["base_query_id"], profile["expert_id"])]
                statuses_for = {}
                reasons = []
                for field, rule in query["expected_contract"]["hard_constraints"].items():
                    status, reason = check_constraint(profile, field, rule); statuses_for[field] = status
                    if reason: reasons.append(reason)
                eligible = all(s == "SATISFIED" for s in statuses_for.values())
                relevance = base["grade"]
                if relevance >= 2 and eligible: available += 1
                near_miss = relevance >= 2 and not eligible and any(s == "VIOLATED" for s in statuses_for.values())
                hn_class = "structured_constraint_near_miss" if near_miss else None
                row = {"query_id": query["query_id"], "expert_id": profile["expert_id"], "relevance_grade": relevance, "eligible": eligible, "constraint_status": statuses_for, "violation_reason": reasons, "hard_negative_class": hn_class, "evidence_provenance": "v2-canonical-structured-truth", "tier": "Gold"}
                stream.write(json.dumps(row, sort_keys=True) + "\n")
                grades[str(relevance)] += 1; statuses["eligible" if eligible else "ineligible"] += 1
                if hn_class: hard_negative["structured_constraint_near_miss"] += 1
            supply[query["category"]] += available; relevant_eligible[query["query_id"]] = available
        stream.flush(); compressed.close()
    fp = fingerprint(queries, judgement_path)
    strata = Counter(q["category"] for q in queries)
    scarcity = sum(v < 5 for v in relevant_eligible.values())
    manifest = {"dataset_manifest": "v2-realism-full", "dataset_checksum": DATASET_CHECKSUM, "benchmark_extension": VERSION, "benchmark_fingerprint": fp, "query_count": len(queries), "gold_count": len(queries), "silver_count": 0, "strata_counts": dict(sorted(strata.items())), "scarcity_query_count": scarcity, "hard_negative_query_count": sum(q["category"] == "hard_negative" for q in queries), "hard_negative_counts": dict(hard_negative), "hard_negative_candidate_count": sum(hard_negative.values()), "contract_schema_version": "v0.5-retrieval-contract-v1", "projection_version": "v0.5-constraint-projection-v1", "index_identity": "armie-experts-v1-v2-gate55b-bm25-r2 / armie-experts-v1-v2-gate55b-dense-10000", "arms": {"C0": "H2 Dense", "C1": "H2 Dense + native pre-filter", "C2-20": "H2 Dense Top-20 + post-filter", "C2-50": "H2 Dense Top-50 + post-filter", "C2-100": "H2 Dense Top-100 + post-filter"}, "top_k": 5, "recall_k": 10, "seeds": {"extension": SEED, "source_document": 7301, "source_query": 9137}, "judgement_generation": "relevance anchored to immutable v2 structured judgements; eligibility independently evaluated against expected contract", "judgement_file": "judgements.jsonl.gz", "limitations": ["controlled synthetic relevance benchmark", "Gold is independent structured audit, not external human ground truth", "Gate 6 evaluates correct manually constructed contracts, not NL extraction"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    audit = {"manifest": VERSION, "query_count": len(queries), "strata_counts": dict(sorted(strata.items())), "grades": dict(grades), "eligibility_counts": dict(statuses), "hard_negative_query_count": sum(q["category"] == "hard_negative" for q in queries), "hard_negative_counts": dict(hard_negative), "hard_negative_candidate_count": sum(hard_negative.values()), "eligible_supply": {"definition": "relevant_grade >= 2 AND eligible", "per_query": dict(relevant_eligible)}, "scarcity_query_count": scarcity, "relevance_method": "existing immutable structured judgement grade for the base semantic query; not recomputed from constraint eligibility", "eligibility_method": "deterministic contract evaluation over all 10,000 profiles", "gold_silver": {"Gold": "all extension queries; structured contract and audit fields", "Silver": "none in this extension"}, "denominators": {"eligible_recall": "all relevant-and-eligible profiles in each query's 10,000-profile judgement universe", "legitimate_scarcity_rate": f"{scarcity} / {len(queries)} queries", "retrieval_shortfall": "among queries with eligible supply >= 5, executions returning fewer than 5 eligible results / eligible-supply-sufficient executions", "eligible_fill": "returned relevant-and-eligible / min(5, eligible supply), zero-supply reported as not applicable"}}
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
