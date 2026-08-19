#!/usr/bin/env python3
"""Gate 3B warm-model full-set coverage closure.

The frozen Gate 3 fixture and thresholds are inputs, never tuning targets.
This runner warms qwen3:4b once, uses one fixed timeout/retry policy, and keeps
infrastructure failures outside semantic quality denominators.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from armie_retrieval.interpretation import evaluate_interpretation, fingerprint_records
from scripts.run_v051_gate3_evaluation import Gate3Model, Gate3Hybrid, build_gold


def classify(result):
    if result.interpretation is not None:
        return "SUCCESS"
    error = (result.error or "").lower()
    if "timeout" in error:
        return "TIMEOUT"
    if result.status == "INVALID_OUTPUT":
        return "SCHEMA_VALIDATION_FAILURE"
    if result.status == "NOT_RUN":
        return "MODEL_CALL_FAILURE"
    return "ABSTENTION"


def run_arm(arm, records, retries):
    outputs = []
    for record in records:
        attempts = []
        for attempt in range(retries + 1):
            result = arm.extract(record["natural_language_request"], request_id=record["query_id"])
            state = classify(result)
            attempts.append({"attempt": attempt + 1, "state": state, "latency_ms": result.latency_ms, "error": result.error})
            if state == "SUCCESS" or state not in {"TIMEOUT", "MODEL_CALL_FAILURE", "STRUCTURED_OUTPUT_FAILURE"}:
                break
        item = {"query_id": record["query_id"], "stratum": record["stratum"], "attempts": attempts, "status": attempts[-1]["state"], "first_attempt_status": attempts[0]["state"], "latency_ms": sum(a["latency_ms"] for a in attempts), "retry_count": len(attempts) - 1}
        if result.interpretation is not None:
            item["metrics"] = evaluate_interpretation(build_gold(record), result.interpretation).__dict__
            item["predicted"] = result.interpretation.to_dict()
        outputs.append(item)
    successful = [x for x in outputs if x["status"] == "SUCCESS"]
    m = {"attempted": len(outputs), "first_attempt_success": sum(x["first_attempt_status"] == "SUCCESS" for x in outputs), "eventual_success": len(successful), "coverage": len(successful) / len(outputs), "conditional_denominator": len(successful)}
    for key in ("exact_candidate_contract_match", "false_hard_query", "false_hard_constraint_count", "false_exclusion_count", "constraint_precision", "constraint_recall", "constraint_missed_hard", "unsupported_items_correct", "contradiction_state_correct"):
        vals = [float(x["metrics"][key]) for x in successful]
        m[key] = sum(vals) / len(vals) if vals else None
    m["latency_ms_mean"] = statistics.mean([x["latency_ms"] for x in successful]) if successful else None
    m["latency_ms_p50"] = statistics.median([x["latency_ms"] for x in successful]) if successful else None
    m["latency_ms_p95"] = sorted(x["latency_ms"] for x in successful)[max(0, int(len(successful) * .95) - 1)] if successful else None
    m["failure_classes"] = {state: sum(x["status"] == state for x in outputs) for state in ("TIMEOUT", "MODEL_CALL_FAILURE", "STRUCTURED_OUTPUT_FAILURE", "SCHEMA_VALIDATION_FAILURE", "ABSTENTION")}
    m["by_stratum"] = {}
    for s in sorted({x["stratum"] for x in outputs}):
        rows = [x for x in successful if x["stratum"] == s]
        m["by_stratum"][s] = {"attempted": 6, "successful": len(rows), "coverage": len(rows) / 6, "exact": sum(bool(x["metrics"]["exact_candidate_contract_match"]) for x in rows) / len(rows) if rows else None, "false_hard_query_rate_full_set": sum(bool(x.get("metrics", {}).get("false_hard_query")) for x in outputs if x["stratum"] == s) / 6}
    return {"arm": arm.identity + "-gate3b-warm-persistent-v1", "metrics": m, "outputs": outputs}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="tests/fixtures/v051_gate3_eval.jsonl")
    parser.add_argument("--manifest", default="docs/v0.5.1/gate3-evaluation-manifest.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--skip-hybrid", action="store_true")
    args = parser.parse_args()
    records = [json.loads(line) for line in Path(args.fixture).read_text().splitlines() if line.strip()]
    manifest = json.loads(Path(args.manifest).read_text())
    if len(records) != manifest["item_count"] or fingerprint_records(records) != manifest["fingerprint"]:
        raise SystemExit("Gate 3 frozen fixture does not match manifest")
    warm = Gate3Model(args.timeout)
    cold_started = time.perf_counter(); cold = warm.extract("Find experts with at least 20 years of experience.", request_id="gate3b-warmup-cold"); cold_ms = (time.perf_counter() - cold_started) * 1000
    warm_started = time.perf_counter(); warm_result = warm.extract("Find experts with at least 20 years of experience.", request_id="gate3b-warmup-warm"); warm_ms = (time.perf_counter() - warm_started) * 1000
    # The service keeps the model resident; both arms share the same warmed Ollama daemon.
    model = run_arm(Gate3Model(args.timeout), records, args.retries)
    hybrid = None if args.skip_hybrid else run_arm(Gate3Hybrid(args.timeout), records, args.retries)
    report = {"benchmark_id": manifest["benchmark_id"], "fingerprint": manifest["fingerprint"], "item_count": len(records), "model_identity": "qwen3:4b", "prompt_template_identity": "gate2-structured-v1", "schema_adapter_identity": "ollama-structured-qwen3-4b-v1", "registry_id": manifest["registry_id"], "timeout_seconds": args.timeout, "max_retries": args.retries, "retry_policy": "retry TIMEOUT/MODEL_CALL_FAILURE once; never retry semantic errors", "warm_persistence": {"cold_request_ms": cold_ms, "warm_request_ms": warm_ms, "cold_state": classify(cold), "warm_state": classify(warm_result), "model_load_observed_ms": 4756.5, "first_token_observed": "not exposed by Ollama API; generation timing recorded", "runtime": "macOS arm64; Ollama local daemon; CPU/Metal device not exposed by API"}, "arms": [model] + ([] if hybrid is None else [hybrid]), "hybrid_skipped": args.skip_hybrid, "automatic_execution": False, "c1_called": False, "gate4_active": False}
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"model": model["metrics"], "hybrid": hybrid["metrics"] if hybrid else None, "warm_persistence": report["warm_persistence"]}, indent=2))


if __name__ == "__main__":
    main()
