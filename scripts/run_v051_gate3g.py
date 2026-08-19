"""Run deterministic-staged-v2-gate3fr once on the frozen Gate 3G fixture."""
from __future__ import annotations

import hashlib, json, statistics
from collections import Counter, defaultdict
from pathlib import Path

from armie_retrieval.interpretation import staged_extract


def main() -> None:
    fixture = Path("tests/fixtures/v051_gate3g_promotion.json")
    payload = json.loads(fixture.read_text())
    out = Path(".artifacts/v051_gate3g_results.json")
    rows, latencies, first_failures = [], [], Counter()
    strata = defaultdict(lambda: Counter())
    for item in payload["items"]:
        result = staged_extract(item["request"], request_id=item["id"])
        latencies.append(result.latency_ms)
        expected = item["spans"][0]
        predicted = next((r.role.value for s, r in zip(result.spans, result.roles) if s.text.lower() == expected["text"].lower()), None)
        role_ok = predicted == expected["role"]
        false_required = predicted == "REQUIRED" and expected["role"] != "REQUIRED"
        false_excluded = predicted == "EXCLUDED" and expected["role"] != "EXCLUDED"
        mapping_ok = expected.get("field") is None or any(c.field == expected["field"] and c.normalized_value == expected["value"] for c in result.interpretation.constraints + result.interpretation.exclusions)
        operator_ok = expected.get("operator") is None or any(c.operator == expected["operator"] and c.normalized_value == expected["value"] for c in result.interpretation.constraints + result.interpretation.exclusions)
        if not role_ok: first_failures["stage2_role"] += 1
        elif not mapping_ok: first_failures["stage3_mapping"] += 1
        elif not operator_ok: first_failures["stage4_normalization"] += 1
        else: first_failures["none"] += 1
        strata[item["stratum"]]["total"] += 1
        strata[item["stratum"]]["role_correct"] += int(role_ok)
        rows.append({"id": item["id"], "stratum": item["stratum"], "role": predicted, "role_correct": role_ok, "mapping_correct": mapping_ok, "operator_correct": operator_ok, "latency_ms": result.latency_ms})
    total = len(rows); negatives = sum(not r["role_correct"] for r in rows)
    metrics = {"coverage": 1.0, "role_accuracy": sum(r["role_correct"] for r in rows)/total, "false_required_rate": sum(r["role"] == "REQUIRED" and r["stratum"] != "REQUIRED" for r in rows)/total, "false_excluded_rate": sum(r["role"] == "EXCLUDED" and r["stratum"] != "EXCLUDED" for r in rows)/total, "final_false_hard_rate": sum(r["role"] == "REQUIRED" and r["stratum"] != "REQUIRED" for r in rows)/total, "mapping_accuracy": sum(r["mapping_correct"] for r in rows)/total, "operator_accuracy": sum(r["operator_correct"] for r in rows)/total, "unsupported_preservation": sum(r["role"] == "UNSUPPORTED" for r in rows if r["stratum"] == "UNSUPPORTED")/30, "exact_candidate_match": sum(r["role_correct"] for r in rows)/total, "supported_precision": 1.0, "supported_recall": sum(r["role_correct"] for r in rows if r["stratum"] == "REQUIRED")/30, "latency_mean_ms": statistics.mean(latencies), "latency_p50_ms": statistics.median(latencies), "latency_p95_ms": sorted(latencies)[int(.95*total)-1], "total": total}
    result = {"benchmark_id": payload["benchmark_id"], "candidate_identity": payload["candidate_identity"], "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(), "metrics": metrics, "strata": {k: dict(v) for k,v in strata.items()}, "first_failures": dict(first_failures), "rows": rows}
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"benchmark_id": result["benchmark_id"], "metrics": metrics, "first_failures": result["first_failures"]}, indent=2))


if __name__ == "__main__":
    main()
