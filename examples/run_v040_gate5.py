"""Run the Gate 5 Gold/Silver relevance benchmark through ARMIE runtime."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_v040_gate4 as gate4  # shared runtime composition, not a second pipeline

from armie_retrieval.benchmarks import benchmark_metrics
from armie_retrieval.benchmarks.failures import FailureCode, classify_failure
from armie_retrieval.benchmarks.relevance import audit_tier, grade_map, select_gold_queries
from armie_retrieval.datasets import load_dataset, validate_dataset
from armie_retrieval.models import Query
from armie_retrieval.observability import trace_query
from armie_retrieval.planners import RuleBasedPlanner
from armie_retrieval.rerankers import BGECrossEncoderReranker, MetadataBoostReranker
from armie_retrieval.relevance import generate_benchmark_queries


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round((len(ordered) - 1) * fraction)))]


def make_profile(profile_id: str, index: str):
    strategy = {"H1": "sparse", "H2": "dense", "H3": "hybrid", "H4": "hybrid"}[profile_id]
    bge = profile_id == "H4"
    reranker = BGECrossEncoderReranker(isolated=False) if bge else MetadataBoostReranker()
    if bge:
        reranker.validate_model_available()
    runtime, retrievers, processor = gate4._runtime(index, reranker)
    planner = RuleBasedPlanner(
        retrievers.capabilities(), strategy_override=strategy,
        processor_names=("deduplicate", "rerank"), parameters=gate4.BOUNDARIES,
    )
    processor.selection = type("Selection", (), {
        "requested": "bge_cross_encoder" if bge else "metadata_boost",
        "actual": "bge_cross_encoder" if bge else "metadata_boost",
        "requested_model": getattr(reranker, "model_name", None),
        "fallback_reason": None,
    })()
    return runtime, planner


def run_tier(tier: str, queries, profiles, index: str) -> dict:
    rows_by_profile: dict[str, list[dict]] = {}
    grade_maps = {query.query_id: grade_map(query, profiles, tier="gold" if tier == "gold" else "silver") for query in queries}
    for profile_id in ("H1", "H2", "H3", "H4"):
        runtime, planner = make_profile(profile_id, index)
        rows: list[dict] = []
        for query in queries:
            request = Query(query.query_text, top_k=5, request_id=f"gate5-{tier}-{profile_id}-{query.query_id}")
            started = time.perf_counter()
            result, trace = trace_query(runtime, planner, request, query_id=request.request_id)
            grades = grade_maps[query.query_id]
            ids = [item.id for item in result.items]
            metrics = benchmark_metrics(ids, grades)
            failures = list(classify_failure(query.query_text, ids, {key: value.grade for key, value in grades.items()}, stage="dense" if profile_id == "H2" else "retrieval"))
            if query.category.value == "hard_negative" and metrics["hard_negative_intrusion_rate"]:
                failures.append(FailureCode.constraint_violation)
            rows.append({
                "query_id": query.query_id, "category": query.category.value, "query_text": query.query_text,
                "profile_id": profile_id, "tier": tier, "result_ids": ids,
                "metrics": metrics, "failures": sorted({failure.value for failure in failures}),
                "trace": trace.to_dict(), "elapsed_ms": (time.perf_counter() - started) * 1000,
                "grade3_ids": [key for key, value in grades.items() if value.grade == 3][:100],
                "judgement_evidence": {key: grades[key].model_dump(mode="json") for key in ids},
            })
        rows_by_profile[profile_id] = rows
    return {"tier": tier, "rows_by_profile": rows_by_profile, "audit": audit_tier(profiles, queries, grade_maps)}


def summarize(run: dict) -> dict:
    profile_summary = {}
    for profile_id, rows in run["rows_by_profile"].items():
        metric_names = ("precision_at_5", "recall_at_10", "recall_at_10_grade_ge_2", "judged_recall_at_10", "grade_3_hit_at_10", "mrr", "ndcg_at_5", "grade_3_hit_rate", "hard_negative_intrusion_rate", "required_constraint_satisfaction_rate", "prohibited_constraint_violation_rate")
        global_metrics = {name: statistics.mean(float(row["metrics"][name]) for row in rows) for name in metric_names}
        by_category: dict[str, dict[str, float]] = {}
        for category in sorted({row["category"] for row in rows}):
            subset = [row for row in rows if row["category"] == category]
            by_category[category] = {name: statistics.mean(float(row["metrics"][name]) for row in subset) for name in metric_names}
        timing_rows = [row["trace"]["timing_ms"] for row in rows]
        reranker_rows = [row["trace"]["reranking"] for row in rows if row["trace"].get("reranking")]
        stage_latency = {}
        for stage in ("retrieval", "fusion", "reranker_model_load", "reranker_inference", "reranking", "end_to_end"):
            values = [float(timing.get(stage, 0.0)) for timing in timing_rows]
            stage_latency[stage] = {"mean": statistics.mean(values), "p50": percentile(values, .5), "p95": percentile(values, .95)}
        warm_timing = timing_rows[1:] if len(timing_rows) > 1 else []
        cold_timing = timing_rows[:1]
        stage_latency["cold"] = {stage: float(cold_timing[0].get(stage, 0.0)) for stage in ("reranker_model_load", "reranker_inference", "reranking", "end_to_end")} if cold_timing else {}
        stage_latency["warm"] = {
            stage: {"mean": statistics.mean(float(timing.get(stage, 0.0)) for timing in warm_timing), "p50": percentile([float(timing.get(stage, 0.0)) for timing in warm_timing], .5), "p95": percentile([float(timing.get(stage, 0.0)) for timing in warm_timing], .95)}
            for stage in ("reranker_model_load", "reranker_inference", "reranking", "end_to_end")
        } if warm_timing else {}
        profile_summary[profile_id] = {
            "query_count": len(rows), "global_metrics": global_metrics, "category_metrics": by_category,
            "latency_ms": stage_latency,
            "reranker_latency_ms": {
                "cold_model_load": max((float(row["model_load_latency_ms"]) for row in reranker_rows), default=0.0),
                "warm_model_load": statistics.mean([float(row["model_load_latency_ms"]) for row in reranker_rows[1:]]) if len(reranker_rows) > 1 else 0.0,
                "warm_inference_p50": percentile([float(row["inference_latency_ms"]) for row in reranker_rows[1:]], .5),
                "warm_inference_p95": percentile([float(row["inference_latency_ms"]) for row in reranker_rows[1:]], .95),
            },
        }
    comparisons = {}
    for left, right in (("H1", "H2"), ("H1", "H3"), ("H3", "H4")):
        left_rows = {row["query_id"]: row for row in run["rows_by_profile"][left]}
        right_rows = {row["query_id"]: row for row in run["rows_by_profile"][right]}
        wins = ties = losses = 0
        deltas = []
        for query_id in left_rows:
            l = float(left_rows[query_id]["metrics"]["ndcg_at_5"]); r = float(right_rows[query_id]["metrics"]["ndcg_at_5"])
            deltas.append({"query_id": query_id, "left_minus_right_ndcg_at_5": l - r})
            if l > r: wins += 1
            elif l < r: losses += 1
            else: ties += 1
        comparisons[f"{left}_vs_{right}"] = {"wins": wins, "ties": ties, "losses": losses, "per_query_ndcg_deltas": deltas}
    failures = []
    for profile_id, rows in run["rows_by_profile"].items():
        for row in rows:
            if row["failures"]:
                failures.append({"query_id": row["query_id"], "category": row["category"], "profile": profile_id, "stage": "retrieval_or_ranking", "failure_codes": row["failures"], "expected_grade3_ids": row["grade3_ids"][:10], "returned_ids": row["result_ids"], "evidence": row["judgement_evidence"]})
    return {"profiles": profile_summary, "comparisons": comparisons, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="/tmp/armie-v040-dataset-full")
    parser.add_argument("--index", default="armie-experts-v1-gate23b-20260803")
    parser.add_argument("--output", default="/tmp/armie-v040-gate5")
    args = parser.parse_args()
    root = Path(args.output); root.mkdir(parents=True, exist_ok=True)
    profiles = load_dataset(args.dataset); validate_dataset(args.dataset)
    queries = generate_benchmark_queries()
    gold = select_gold_queries(queries)
    silver_ids = {query.query_id for query in queries} - {query.query_id for query in gold}
    silver = tuple(query for query in queries if query.query_id in silver_ids)
    gate4.EMBEDDING = gate4.BGEEmbeddingProvider(); gate4.EMBEDDING.validate_model_available()
    output = {"dataset_manifest": validate_dataset(args.dataset).model_dump(mode="json"), "embedding_model": gate4.EMBEDDING.model_name, "index": args.index, "candidate_boundaries": gate4.BOUNDARIES, "gold": run_tier("gold", gold, profiles, args.index), "silver": run_tier("silver", silver, profiles, args.index)}
    output["gold"]["summary"] = summarize(output["gold"]); output["silver"]["summary"] = summarize(output["silver"])
    (root / "gate5-benchmark.json").write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(root / "gate5-benchmark.json"), "gold_queries": len(gold), "silver_queries": len(silver), "profiles": ["H1", "H2", "H3", "H4"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
