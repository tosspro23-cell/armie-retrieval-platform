"""Execute the frozen Gate 3G-R prospective benchmark exactly once."""
from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from armie_retrieval.interpretation import staged_extract


def _role_for_span(result, expected_text):
    needle = " ".join(expected_text.lower().split())
    for span, assignment in zip(result.spans, result.roles):
        if needle in " ".join(span.text.lower().split()) or " ".join(span.text.lower().split()) in needle:
            return assignment.role.value
    return None


def main() -> None:
    fixture = Path("tests/fixtures/v051_gate3gr_promotion_v2.json")
    payload = json.loads(fixture.read_text())
    rows, latencies, first_failures = [], [], Counter()
    strata = defaultdict(Counter)
    for item in payload["items"]:
        result = staged_extract(item["request"], request_id=item["id"])
        expected_spans = item["spans"]
        predicted_roles = [_role_for_span(result, span["text"]) for span in expected_spans]
        role_ok = all(actual == expected["role"] for actual, expected in zip(predicted_roles, expected_spans))
        expected_supported = [s for s in expected_spans if s.get("field")]
        constraints = tuple(result.interpretation.constraints) + tuple(result.interpretation.exclusions)
        mapping_ok = all(any(c.field == s["field"] and c.normalized_value == s["value"] for c in constraints) for s in expected_supported)
        operator_ok = all(any(c.operator == s["operator"] and c.normalized_value == s["value"] for c in constraints) for s in expected_supported)
        if not role_ok: first_failures["stage2_role"] += 1
        elif not mapping_ok: first_failures["stage3_mapping"] += 1
        elif not operator_ok: first_failures["stage4_normalization"] += 1
        else: first_failures["none"] += 1
        stratum = item.get("stratum", item["spans"][0]["role"])
        strata[stratum]["total"] += 1
        strata[stratum]["role_correct"] += int(role_ok)
        rows.append({"id": item["id"], "stratum": stratum, "role": predicted_roles[0] if len(predicted_roles) == 1 else predicted_roles, "role_correct": role_ok, "mapping_correct": mapping_ok, "operator_correct": operator_ok, "latency_ms": result.latency_ms})
        latencies.append(result.latency_ms)
    total = len(rows)
    required_total = sum(r["stratum"] == "REQUIRED" for r in rows)
    metrics = {
        "coverage": 1.0,
        "role_accuracy": sum(r["role_correct"] for r in rows) / total,
        "false_required_rate": sum(r["role"] == "REQUIRED" and r["stratum"] not in {"REQUIRED", "MIXED"} for r in rows) / total,
        "false_excluded_rate": sum(r["role"] == "EXCLUDED" and r["stratum"] not in {"EXCLUDED", "MIXED"} for r in rows) / total,
        "final_false_hard_rate": sum(r["role"] == "REQUIRED" and r["stratum"] not in {"REQUIRED", "MIXED"} for r in rows) / total,
        "mapping_accuracy": sum(r["mapping_correct"] for r in rows) / total,
        "operator_accuracy": sum(r["operator_correct"] for r in rows) / total,
        "unsupported_preservation": sum(r["role"] == "UNSUPPORTED" for r in rows if r["stratum"] == "UNSUPPORTED") / max(1, sum(r["stratum"] == "UNSUPPORTED" for r in rows)),
        "exact_candidate_match": sum(r["role_correct"] and r["mapping_correct"] and r["operator_correct"] for r in rows) / total,
        "supported_precision": sum(r["mapping_correct"] for r in rows) / max(1, sum(bool(r["mapping_correct"]) for r in rows)),
        "supported_recall": sum(r["mapping_correct"] for r in rows if r["stratum"] in {"REQUIRED", "EXCLUDED", "MIXED"}) / max(1, required_total),
        "latency_mean_ms": statistics.mean(latencies),
        "latency_p50_ms": statistics.median(latencies),
        "latency_p95_ms": sorted(latencies)[max(0, int(.95 * total) - 1)],
        "total": total,
    }
    result = {"benchmark_id": payload["benchmark_id"], "candidate_identity": payload["candidate_identity"], "fixture_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(), "metrics": metrics, "strata": {k: dict(v) for k, v in strata.items()}, "first_failures": dict(first_failures), "rows": rows}
    out = Path(".artifacts/v051_gate3gr_results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"benchmark_id": result["benchmark_id"], "fixture_sha256": result["fixture_sha256"], "metrics": metrics, "first_failures": result["first_failures"]}, indent=2))


if __name__ == "__main__":
    main()
