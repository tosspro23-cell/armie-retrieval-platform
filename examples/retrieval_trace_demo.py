"""Run deterministic or model-enhanced retrieval traces over the bounded benchmark."""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.benchmarking import generate_benchmark_dataset
from armie_retrieval.models import Query
from armie_retrieval.observability import export_trace, render_terminal, trace_query
from armie_retrieval.processors import DeduplicateProcessor, MetadataFilterProcessor, QueryAwareRerankProcessor
from armie_retrieval.profiles import apply_overrides, load_profile
from armie_retrieval.providers import InMemoryKnowledgeProvider, NetworkXKnowledgeGraphProvider
from armie_retrieval.registries import ProcessorRegistry, RetrieverRegistry
from armie_retrieval.retrievers import DenseRetriever, GraphRetriever, HybridRetriever, SparseRetriever
from armie_retrieval.runtime import RetrievalRuntime
from armie_retrieval.runtime_profiles import select_planner, select_reranker


def build_portable_runtime(experts, reranker_selection):
    """Portable retrievers preserve model-free fixture execution; reranking is explicit."""
    provider = InMemoryKnowledgeProvider(experts)
    dense, keyword = DenseRetriever(provider), SparseRetriever(provider)
    retrievers = RetrieverRegistry()
    retrievers.register("dense", dense, capabilities={"dense"}, version="0.2.3", priority=100)
    retrievers.register("keyword", keyword, capabilities={"sparse"}, version="0.2.3", priority=100)
    retrievers.register("hybrid", HybridRetriever(dense, keyword), capabilities={"hybrid"}, version="0.2.3", priority=100)
    retrievers.register("graph", GraphRetriever(NetworkXKnowledgeGraphProvider.from_experts(experts)), capabilities={"graph"}, version="0.2.3", priority=100)
    rerank = QueryAwareRerankProcessor(reranker_selection.provider, name="rerank")
    rerank.selection = reranker_selection
    processors = ProcessorRegistry()
    for processor in (DeduplicateProcessor(), MetadataFilterProcessor(), rerank):
        processors.register(processor.name, processor, capabilities={processor.name}, version="0.2.3")
    return RetrievalRuntime(retrievers, processors), retrievers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--query-id", help="One of the generated benchmark query IDs")
    group.add_argument("--query", help="Arbitrary expert-discovery question")
    parser.add_argument("--profile", choices=("fixture", "baseline", "model-enhanced"), default="fixture")
    parser.add_argument("--planner", choices=("rule-based", "ollama"))
    parser.add_argument("--planner-model")
    parser.add_argument("--reranker", choices=("none", "metadata", "bge"))
    parser.add_argument("--reranker-model")
    parser.add_argument("--reranker-device", choices=("auto", "cpu", "mps"))
    parser.add_argument("--reranker-batch-size", type=int)
    parser.add_argument("--rerank-candidates", type=int)
    parser.add_argument("--top-k", type=int, help="Final Top-K; takes precedence over profile configuration")
    parser.add_argument("--mode", choices=("dense", "keyword", "graph", "hybrid"), help="Explicit retrieval ablation")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--export-json", action="store_true")
    parser.add_argument("--artifact-dir", default=".artifacts/traces")
    parser.add_argument("--work-dir", default=".artifacts/trace-demo")
    args = parser.parse_args()

    candidate_override = {"rerank_candidate_k": args.rerank_candidates}
    if args.top_k is not None:
        candidate_override.update({"final_top_k": args.top_k, "effective_top_k_source": "cli"})
    profile = apply_overrides(
        load_profile(args.profile),
        planner={"type": args.planner, "model": args.planner_model},
        reranker={"type": args.reranker, "model": args.reranker_model, "device": args.reranker_device, "batch_size": args.reranker_batch_size},
        candidate_pool=candidate_override,
    )
    root = Path(args.work_dir)
    if root.exists():
        shutil.rmtree(root)
    dataset = generate_benchmark_dataset(root, size=50)
    cases = {case["id"]: case for case in dataset.queries}
    if args.query_id:
        if args.query_id not in cases:
            parser.error(f"Unknown query id. Available: {', '.join(cases)}")
        case = cases[args.query_id]
        text, relevant_ids, query_id = case["query"], set(case["relevant_ids"]), case["id"]
    else:
        text, relevant_ids, query_id = args.query or dataset.queries[0]["query"], None, "interactive-query"

    reranker_selection = select_reranker(profile)
    runtime, retrievers = build_portable_runtime(dataset.experts, reranker_selection)
    planner_selection = select_planner(profile, capabilities=retrievers.capabilities())
    planner = planner_selection.planner
    query = Query(text, top_k=int(profile.get("candidate_pool", {}).get("final_top_k", 5)))
    if args.mode:
        original_plan = planner.plan(query)
        strategy = "sparse" if args.mode == "keyword" else args.mode

        class FixedPlanPlanner:
            selection = type("Selection", (), {"requested": "fixed_plan", "actual": "fixed_plan", "requested_model": None, "fallback_enabled": False, "fallback_reason": "CLI ablation override"})()

            def plan(self, ignored_query):
                return replace(original_plan, strategy=strategy)

        planner = FixedPlanPlanner()
    _, trace = trace_query(
        runtime, planner, query, query_id=query_id, relevant_ids=relevant_ids,
        evaluation_cutoffs=tuple(profile.get("evaluation", {}).get("cutoffs", (1, 2, 3, 5, 10))),
    )
    print(render_terminal(trace, verbose=args.verbose))
    if args.export_json:
        print(f"\nJSON trace: {export_trace(trace, args.artifact_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
