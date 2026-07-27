"""Controlled planner-model ablation for ARMIE Retrieval Platform v0.2.3.

``planner-only`` evaluates planning decisions only.  ``full-pipeline`` keeps
the dataset and every downstream setting fixed while varying only the planner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.benchmarking import generate_benchmark_dataset
from armie_retrieval.models import Query
from armie_retrieval.observability import capture_plan, export_trace, trace_query
from armie_retrieval.profiles import apply_overrides, load_profile
from armie_retrieval.runtime_profiles import select_planner, select_reranker
from retrieval_trace_demo import build_portable_runtime


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()[:16]


def execution_context(profile, dataset, *, reranker_selection) -> dict:
    pool = profile.get("candidate_pool", {})
    context = {
        "profile": profile["name"], "dataset_seed": 0, "dataset_fingerprint": fingerprint(dataset.experts),
        "index_fingerprints": {"dense": fingerprint([item.id for item in dataset.experts]), "keyword": fingerprint([item.content for item in dataset.experts]), "graph": fingerprint([(item.id, item.metadata.get("organization")) for item in dataset.experts])},
        "embedding_provider": profile.get("embedding", {}).get("type", "deterministic_hash"),
        "embedding_model": profile.get("embedding", {}).get("model", "n/a"),
        "dense_retriever": "DenseRetriever", "sparse_retriever": "SparseRetriever", "graph_retriever": "GraphRetriever",
        "fusion_method": "reciprocal_rank_fusion", "rrf_k": 60,
        "reranker_provider": reranker_selection.requested, "reranker_model": reranker_selection.requested_model,
        "reranker_device_policy": profile.get("reranker", {}).get("device", "n/a"), "reranker_batch_size": profile.get("reranker", {}).get("batch_size", "n/a"),
        "retrieval_candidate_k": int(pool.get("retrieval_candidate_k", 20)), "rerank_candidate_k": int(pool.get("rerank_candidate_k", 20)),
        "final_top_k": int(pool.get("final_top_k", 5)), "evaluation_cutoffs": profile.get("evaluation", {}).get("cutoffs", []),
        "fallback_policy": {"planner": profile.get("planner", {}).get("fallback"), "reranker": profile.get("reranker", {}).get("fallback")},
    }
    context["execution_context_fingerprint"] = fingerprint(context)
    return context


def plan_fingerprint(plan) -> str:
    payload = asdict(plan)
    payload.pop("plan_id", None)
    return fingerprint(payload)


def summarize(rows: list[dict]) -> dict:
    """Backward-compatible evidence summary for callers of the v0.2.3 script."""
    per_model = {}
    for model in sorted({row["model"] for row in rows}):
        selected = [row for row in rows if row["model"] == model]
        per_model[model] = {
            "plan_valid_rate": sum(bool(row.get("plan_valid")) for row in selected) / len(selected),
            "average_planner_latency_ms": mean(row["planner_latency_ms"] for row in selected),
        }
    return {"per_model": per_model, "recommendation": "keep qwen3:4b default"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("planner-only", "full-pipeline"), default="planner-only")
    parser.add_argument("--profile", choices=("fixture", "baseline", "model-enhanced"), default="model-enhanced")
    parser.add_argument("--models", nargs="+", default=("qwen3:4b", "qwen3:8b"))
    parser.add_argument("--reranker", choices=("none", "metadata", "bge"))
    parser.add_argument("--reranker-model")
    parser.add_argument("--query-id", default="healthcare-azure-ai")
    parser.add_argument("--export-json", action="store_true")
    parser.add_argument("--artifact-dir", default=".artifacts/ablation")
    parser.add_argument("--work-dir", default=".artifacts/planner-ablation")
    args = parser.parse_args()
    root = Path(args.work_dir)
    if root.exists():
        shutil.rmtree(root)
    dataset = generate_benchmark_dataset(root, size=50)
    cases = {case["id"]: case for case in dataset.queries}
    if args.query_id not in cases:
        parser.error(f"Unknown query ID. Available: {', '.join(cases)}")
    profile = apply_overrides(load_profile(args.profile), reranker={"type": args.reranker, "model": args.reranker_model})
    reranker_selection = select_reranker(profile)
    context = execution_context(profile, dataset, reranker_selection=reranker_selection)
    reports, traces = [], []
    case = cases[args.query_id]
    for model in args.models:
        model_profile = apply_overrides(profile, planner={"model": model})
        # Build the same in-memory indexes and runtime configuration for every model.
        runtime, retrievers = build_portable_runtime(dataset.experts, reranker_selection)
        planner_selection = select_planner(model_profile, capabilities=retrievers.capabilities())
        planner = planner_selection.planner
        query = Query(str(case["query"]), top_k=context["final_top_k"])
        if args.mode == "planner-only":
            plan, plan_trace = capture_plan(planner, query)
            reports.append({"mode": args.mode, "model": model, "plan_valid": bool(plan.strategy), "requested_planner": plan_trace.requested_provider, "actual_planner": plan_trace.actual_provider, "requested_reranker": reranker_selection.requested, "actual_reranker": "not_executed", "planner_fallback": plan_trace.fallback_reason, "reranker_fallback": None, "plan_fingerprint": plan_fingerprint(plan), "strategy": plan.strategy, "retrievers": list(plan_trace.selected_retrievers), "processors": list(plan.processor_names), "reason_codes": list(plan_trace.reason_codes), "constraint_types": list(plan_trace.constraint_types), "routing_warnings": list(plan_trace.warnings), "planner_latency_ms": plan_trace.latency_ms, "metrics": None})
            continue
        result, trace = trace_query(runtime, planner, query, query_id=str(case["id"]), relevant_ids=set(case["relevant_ids"]), evaluation_cutoffs=tuple(context["evaluation_cutoffs"]))
        reports.append({"mode": args.mode, "model": model, "plan_valid": bool(trace.planner.selected_strategy), "requested_planner": trace.planner.requested_provider, "actual_planner": trace.planner.actual_provider, "requested_reranker": reranker_selection.requested, "actual_reranker": trace.reranking.actual_provider if trace.reranking else "not_executed", "planner_fallback": trace.planner.fallback_reason, "reranker_fallback": trace.reranking.fallback_diagnostic if trace.reranking else None, "plan_fingerprint": fingerprint({key: value for key, value in trace.planner.parsed_plan.items() if key != "plan_id"}), "final_results": [item.id for item in result.items], "metrics": trace.evaluation.metrics if trace.evaluation else None, "planner_latency_ms": trace.planner.latency_ms})
        traces.append(trace)
    output = {"mode": args.mode, "models": list(args.models), "execution_context": context, "results": reports, "summary": {"mode": args.mode, "planner_only": args.mode == "planner-only", "downstream_metrics_reported": args.mode == "full-pipeline", "average_planner_latency_ms": {model: mean(row["planner_latency_ms"] for row in reports if row["model"] == model) for model in args.models}}}
    print(json.dumps(output, indent=2, sort_keys=True))
    if args.export_json:
        destination = Path(args.artifact_dir); destination.mkdir(parents=True, exist_ok=True)
        report = destination / "planner-ablation.json"; report.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
        for trace in traces: export_trace(trace, destination / "traces")
        print(f"Ablation report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
