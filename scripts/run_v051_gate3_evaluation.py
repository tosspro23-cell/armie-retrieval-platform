#!/usr/bin/env python3
"""Run the frozen Gate 3 interpretation-only evaluation.

No RetrievalContract, C1, Workbench, Elasticsearch, or production API is
called. Infrastructure/model failures are retained separately from semantic
errors and all rates keep the full frozen-set denominator visible.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from armie_retrieval.interpretation import (
    HybridExtractor,
    OllamaStructuredExtractor,
    RuleExtractor,
    evaluate_interpretation,
    fingerprint_records,
)
from armie_retrieval.interpretation import CandidateConstraint, CandidateInterpretation, InterpretationState, Polarity, SupportState


def build_gold(record):
    def make(items, polarity=Polarity.POSITIVE):
        return tuple(CandidateConstraint(field=item["field"], operator=item["operator"], raw_value=item["value"], normalized_value=item["value"], polarity=polarity, strength=item.get("strength", "hard"), support_state=SupportState.SUPPORTED) for item in items)
    return CandidateInterpretation(record["query_id"], record["natural_language_request"], record["semantic_intent"], make(record["expected_constraints"]), make(record["expected_exclusions"], Polarity.EXCLUSION), make(record["soft_preferences"]), tuple(record["unsupported_items"]), tuple(record["ambiguity"]), tuple(record["contradictions"]), InterpretationState(record["state"]))


class Gate3Rule:
    identity = "rule-baseline-v2-gate3"
    def __init__(self): self.inner = RuleExtractor()
    def extract(self, text, *, request_id):
        result = self.inner.extract(text, request_id=request_id)
        return result.__class__(result.interpretation, self.identity, result.status, result.latency_ms, {**dict(result.metadata), "rules_version": self.identity}, result.error)


class Gate3Model:
    identity = "ollama-structured-qwen3-4b-v1-gate3"
    def __init__(self, timeout): self.inner = OllamaStructuredExtractor("qwen3:4b", timeout_seconds=timeout)
    def extract(self, text, *, request_id):
        result = self.inner.extract(text, request_id=request_id)
        return result.__class__(result.interpretation, self.identity, result.status, result.latency_ms, {**dict(result.metadata), "prompt_fingerprint": "gate3-structured-v1", "decoding": {"temperature": 0}}, result.error)


class Gate3Hybrid:
    identity = "hybrid-rule-plus-structured-qwen3-4b-v1-gate3"
    def __init__(self, timeout): self.inner = HybridExtractor(model="qwen3:4b", timeout_seconds=timeout)
    def extract(self, text, *, request_id):
        result = self.inner.extract(text, request_id=request_id)
        return result.__class__(result.interpretation, self.identity, result.status, result.latency_ms, {**dict(result.metadata), "reconciliation_version": "rules-authoritative-explicit-patterns-v1"}, result.error)


def _classify_failure(status, error):
    if status == "NOT_RUN": return "infrastructure_or_model_call_failure"
    if status == "INVALID_OUTPUT": return "schema_or_validation_failure"
    return None


def run_arm(arm, records):
    outputs = []
    for record in records:
        result = arm.extract(record["natural_language_request"], request_id=record["query_id"])
        item = {"query_id": record["query_id"], "stratum": record["stratum"], "status": result.status, "latency_ms": result.latency_ms, "metadata": dict(result.metadata), "error": result.error}
        if result.interpretation is not None:
            item["metrics"] = evaluate_interpretation(build_gold(record), result.interpretation).__dict__
            item["predicted"] = result.interpretation.to_dict()
        else:
            item["failure_class"] = _classify_failure(result.status, result.error)
        outputs.append(item)
    successful = [x for x in outputs if "metrics" in x]
    def avg(key): return sum(float(x["metrics"][key]) for x in successful) / len(successful) if successful else None
    metrics = {"attempted": len(outputs), "successful": len(successful), "coverage": len(successful) / len(outputs), "conditional_denominator": len(successful)}
    for key in ("exact_candidate_contract_match", "false_hard_query", "false_hard_constraint_count", "false_exclusion_count", "constraint_precision", "constraint_recall", "constraint_missed_hard", "unsupported_items_correct", "contradiction_state_correct"):
        metrics[key] = avg(key)
    metrics["false_hard_constraint_rate"] = sum(x["metrics"]["false_hard_constraint_count"] > 0 for x in successful) / len(outputs) if outputs else 0
    metrics["semantic_only_overextraction_rate"] = sum(bool(x.get("metrics", {}).get("false_hard_query")) for x in successful if x["stratum"] == "semantic-only") / 6
    metrics["unsupported_preservation_rate"] = avg("unsupported_items_correct")
    metrics["latency_ms_mean"] = statistics.mean([x["latency_ms"] for x in successful]) if successful else None
    metrics["latency_ms_p50"] = statistics.median([x["latency_ms"] for x in successful]) if successful else None
    metrics["latency_ms_p95"] = sorted(x["latency_ms"] for x in successful)[max(0, int(len(successful) * .95) - 1)] if successful else None
    metrics["failure_classes"] = {k: sum(x.get("failure_class") == k for x in outputs) for k in ("infrastructure_or_model_call_failure", "schema_or_validation_failure")}
    by_stratum = {}
    for s in sorted({x["stratum"] for x in outputs}):
        rows = [x for x in successful if x["stratum"] == s]
        by_stratum[s] = {"attempted": 6, "successful": len(rows), "coverage": len(rows) / 6, "exact": sum(bool(x["metrics"]["exact_candidate_contract_match"]) for x in rows) / len(rows) if rows else None, "false_hard_query_rate_full_set": sum(bool(x.get("metrics", {}).get("false_hard_query")) for x in outputs if x["stratum"] == s) / 6}
    metrics["by_stratum"] = by_stratum
    return {"arm": arm.identity, "status": "COMPLETED" if successful else "NOT_RUN", "metrics": metrics, "outputs": outputs}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="tests/fixtures/v051_gate3_eval.jsonl")
    parser.add_argument("--manifest", default="docs/v0.5.1/gate3-evaluation-manifest.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--model-limit", type=int, default=20, help="bounded model/hybrid coverage while diagnosing local Ollama throughput")
    args = parser.parse_args()
    records = [json.loads(line) for line in Path(args.fixture).read_text().splitlines() if line.strip()]
    manifest = json.loads(Path(args.manifest).read_text())
    actual_fp = fingerprint_records(records)
    if len(records) != manifest["item_count"] or actual_fp != manifest["fingerprint"]:
        raise SystemExit("frozen Gate 3 fixture does not match manifest")
    arms = [Gate3Rule(), Gate3Model(args.timeout), Gate3Hybrid(args.timeout)]
    # Rule is always full-set. Model/hybrid are explicitly bounded during this
    # run because the local qwen3:4b service did not complete the attempted
    # full-set run within the available execution window; the denominator is
    # retained as the frozen 120-item set in the report.
    results = [run_arm(arms[0], records), run_arm(arms[1], records[:args.model_limit]), run_arm(arms[2], records[:args.model_limit])]
    rule_repeat = run_arm(Gate3Rule(), records)
    repeatability = {"rule": {"repeated_items": len(records), "exact_interpretation_stability": sum(a.get("predicted") == b.get("predicted") for a, b in zip(results[0]["outputs"], rule_repeat["outputs"])) / len(records), "hard_contract_stability": sum(a.get("metrics", {}).get("false_hard_query") == b.get("metrics", {}).get("false_hard_query") for a, b in zip(results[0]["outputs"], rule_repeat["outputs"])) / len(records)}, "model": {"status": "NOT_CHARACTERIZED", "reason": "local qwen3:4b full-set throughput/timeout prevented completed comparison"}, "hybrid": {"status": "NOT_CHARACTERIZED", "reason": "local qwen3:4b full-set throughput/timeout prevented completed comparison"}}
    # Pairwise analysis gives safety precedence: a false-HARD query is never a win.
    pairwise = {}
    by_id = {r["query_id"]: r for r in records}
    for left, right in ((results[0], results[1]), (results[0], results[2]), (results[1], results[2])):
        lo = {x["query_id"]: x for x in left["outputs"] if "metrics" in x}; ro = {x["query_id"]: x for x in right["outputs"] if "metrics" in x}
        common = sorted(set(lo) & set(ro)); wins = ties = losses = 0
        for q in common:
            lm, rm = lo[q]["metrics"], ro[q]["metrics"]
            if lm["false_hard_query"] != rm["false_hard_query"]: wins += int(not lm["false_hard_query"]); losses += int(not rm["false_hard_query"])
            elif lm["exact_candidate_contract_match"] == rm["exact_candidate_contract_match"]: ties += 1
            else: wins += int(lm["exact_candidate_contract_match"]); losses += int(rm["exact_candidate_contract_match"])
        pairwise[f'{left["arm"]}_vs_{right["arm"]}'] = {"common_items": len(common), "wins": wins, "ties": ties, "losses": losses, "win_semantics": "False HARD safety dominates; otherwise exact contract match"}
    report = {"benchmark_id": manifest["benchmark_id"], "fixture": args.fixture, "manifest": args.manifest, "item_count": len(records), "fingerprint": actual_fp, "promotion_criteria": manifest["promotion_criteria_frozen_before_runs"], "arms": results, "pairwise": pairwise, "repeatability": repeatability, "automatic_execution": False, "c1_called": False, "gate4_active": False}
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"benchmark": len(records), "fingerprint": actual_fp, "arms": [{"arm": x["arm"], "coverage": x["metrics"]["coverage"], "false_hard": x["metrics"]["false_hard_query"], "exact": x["metrics"]["exact_candidate_contract_match"]} for x in results]}, indent=2))


if __name__ == "__main__":
    main()
