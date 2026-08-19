#!/usr/bin/env python3
"""Run the bounded Gate 2 development-arm comparison.

This script evaluates interpretation only. It never validates into a
RetrievalContract, calls C1, or touches Elasticsearch/Workbench.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from armie_retrieval.interpretation import (
    CandidateConstraint,
    CandidateInterpretation,
    HybridExtractor,
    InterpretationState,
    OllamaStructuredExtractor,
    Polarity,
    RuleExtractor,
    SupportState,
    evaluate_interpretation,
    fingerprint_records,
)
from armie_retrieval.constraints.registry import REGISTRY_ID


def build_gold(record: dict) -> CandidateInterpretation:
    def make(items, polarity=Polarity.POSITIVE):
        return tuple(CandidateConstraint(field=item["field"], operator=item["operator"], raw_value=item["value"], normalized_value=item["value"], polarity=polarity, strength=item.get("strength", "hard"), support_state=SupportState.SUPPORTED) for item in items)
    state = InterpretationState(record["state"])
    return CandidateInterpretation(record["query_id"], record["natural_language_request"], record["semantic_intent"], make(record["expected_constraints"]), make(record["expected_exclusions"], Polarity.EXCLUSION), make(record["soft_preferences"]), tuple(record["unsupported_items"]), tuple(record["ambiguity"]), tuple(record["contradictions"]), state)


def stratum(query_id: str) -> str:
    return query_id.split("-")[0]


def run_arm(arm, records):
    outputs = []
    for record in records:
        result = arm.extract(record["natural_language_request"], request_id=record["query_id"])
        entry = {"query_id": record["query_id"], "status": result.status, "latency_ms": result.latency_ms, "metadata": dict(result.metadata), "error": result.error}
        if result.interpretation is not None:
            evaluation = evaluate_interpretation(build_gold(record), result.interpretation)
            entry["metrics"] = evaluation.__dict__
            entry["predicted"] = result.interpretation.to_dict()
        outputs.append(entry)
    completed = [item for item in outputs if item.get("metrics")]
    metrics = {}
    if completed:
        for key in ("exact_candidate_contract_match", "false_hard_query", "missed_hard_query", "false_exclusion_count", "constraint_precision", "constraint_recall", "constraint_false_positives", "constraint_missed_hard", "unsupported_items_correct", "ambiguity_state_correct", "contradiction_state_correct"):
            values = [item["metrics"][key] for item in completed]
            metrics[key] = sum(values) / len(values) if isinstance(values[0], (int, float)) and not isinstance(values[0], bool) else sum(bool(v) for v in values) / len(values)
        latencies = [item["latency_ms"] for item in completed]
        metrics["latency_ms_mean"] = statistics.mean(latencies)
        metrics["latency_ms_p50"] = statistics.median(latencies)
        metrics["latency_ms_p95"] = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)]
        by_stratum = {}
        for item in completed:
            bucket = stratum(item["query_id"])
            by_stratum.setdefault(bucket, []).append(item["metrics"])
        metrics["by_stratum"] = {bucket: {"count": len(items), "exact_match": sum(bool(x["exact_candidate_contract_match"]) for x in items) / len(items), "false_hard_query_rate": sum(bool(x["false_hard_query"]) for x in items) / len(items), "missed_hard_rate": sum(bool(x["missed_hard_query"]) for x in items) / len(items)} for bucket, items in by_stratum.items()}
    return {"arm": arm.identity, "status": "COMPLETED" if completed else "NOT_RUN", "completed": len(completed), "total": len(records), "metrics": metrics, "outputs": outputs}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="tests/fixtures/v051_gate1_gold.jsonl")
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--model-sample", type=int, default=5, help="bounded model-arm sample; rule arm always runs all items")
    args = parser.parse_args()
    fixture = Path(args.fixture)
    records = [json.loads(line) for line in fixture.read_text().splitlines() if line.strip()]
    rule_records = records
    model_records = records[: max(0, min(args.model_sample, len(records)))]
    arms = [(RuleExtractor(), rule_records), (OllamaStructuredExtractor(args.model, timeout_seconds=20), model_records), (HybridExtractor(model=args.model, timeout_seconds=20), model_records)]
    report = {
        "benchmark_id": "v0.5.1-nl-contract-extraction-v1",
        "fixture": str(fixture),
        "item_count": len(records),
        "fingerprint": fingerprint_records(records),
        "schema_version": "nl-constraint-interpretation-v1",
        "registry_id": REGISTRY_ID,
        "arms": [dict(run_arm(arm, arm_records), sample_scope=("all" if arm_records is records else f"first_{len(arm_records)}_development_items")) for arm, arm_records in arms],
        "automatic_execution": False,
        "c1_called": False,
    }
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"benchmark": report["item_count"], "fingerprint": report["fingerprint"], "arms": [{"arm": arm["arm"], "status": arm["status"], "completed": arm["completed"]} for arm in report["arms"]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
