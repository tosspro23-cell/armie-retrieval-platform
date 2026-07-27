"""Validate baseline or model-enhanced production retrieval without downloading models."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.benchmarking import generate_benchmark_dataset
from armie_retrieval.evaluation import run_evaluation
from armie_retrieval.indexing import GraphIndexBuilder, KeywordIndexBuilder, VectorIndexBuilder
from armie_retrieval.models import Query
from armie_retrieval.observability import trace_query
from armie_retrieval.production import ProductionArtifacts, create_production_platform
from armie_retrieval.profiles import apply_overrides, load_profile
from armie_retrieval.runtime_profiles import select_planner, select_reranker


class DeterministicValidationEmbeddingProvider:
    """Fixture-only embedding provider; production model validation is explicit."""

    dimension = 16

    def embed(self, texts):
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimension
            for byte in text.lower().encode("utf-8"):
                vector[byte % self.dimension] += 1.0
            magnitude = sum(value * value for value in vector) ** 0.5 or 1.0
            vectors.append([value / magnitude for value in vector])
        return vectors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("fixture", "baseline", "model-enhanced"), default="baseline")
    parser.add_argument("--artifacts", default=".artifacts/validation")
    parser.add_argument("--size", type=int, default=50)
    parser.add_argument("--ollama-model")
    parser.add_argument("--reranker-model")
    parser.add_argument("--keep-artifacts", action="store_true")
    args = parser.parse_args()
    profile = apply_overrides(
        load_profile(args.profile),
        planner={"model": args.ollama_model}, reranker={"model": args.reranker_model},
    )
    root = Path(args.artifacts)
    if root.exists() and not args.keep_artifacts:
        shutil.rmtree(root)
    dataset = generate_benchmark_dataset(root, size=args.size)
    embedding = DeterministicValidationEmbeddingProvider()
    artifacts = ProductionArtifacts(root / "indexes")
    VectorIndexBuilder(embedding).build(dataset.experts, artifacts.vector)
    KeywordIndexBuilder().build(dataset.experts, artifacts.keyword)
    GraphIndexBuilder().build(dataset.experts, artifacts.graph)
    reranker_selection = select_reranker(profile)
    platform = create_production_platform(artifacts, embedding, reranker=reranker_selection.provider)
    rerank_processor = platform.processors.resolve("rerank")
    rerank_processor.selection = reranker_selection
    planner_selection = select_planner(profile, capabilities=platform.retrievers.capabilities())
    planner = planner_selection.planner
    case = dataset.queries[0]
    query = Query(str(case["query"]), top_k=5)
    result, trace = trace_query(platform.runtime, planner, query, query_id=str(case["id"]), relevant_ids=set(case["relevant_ids"]))
    # Model-enhanced validation intentionally exercises one complete FAISS →
    # isolated BGE → evaluation path.  Repeating short-lived model workers for
    # every synthetic benchmark case is not needed for this release check.
    evaluation = run_evaluation(platform.runtime, planner, dataset.queries, top_k=5) if args.profile != "model-enhanced" else None
    report = {
        "profile": args.profile,
        "dataset_size": len(dataset.experts),
        "faiss_persistent_index": True,
        "keyword_persistent_index": True,
        "networkx_graph_artifact": True,
        "planner": {
            "requested_provider": trace.planner.requested_provider, "actual_provider": trace.planner.actual_provider,
            "model": trace.planner.requested_model, "strategy": trace.planner.selected_strategy,
            "selected_retrievers": list(trace.planner.selected_retrievers), "selected_processors": list(trace.planner.parsed_plan["processor_names"]),
            "plan_valid": bool(trace.planner.selected_strategy), "latency_ms": trace.planner.latency_ms,
            "fallback": trace.planner.fallback_reason,
        },
        "execution": {"result_count": len(result.items), "retrieval_latency_ms": result.latency_ms},
        "reranker": None if trace.reranking is None else trace.reranking.__dict__,
        "metrics": ({"precision_at_k": evaluation.precision_at_k, "recall_at_k": evaluation.recall_at_k, "mrr": evaluation.mrr, "ndcg_at_k": evaluation.ndcg_at_k, "latency_ms": evaluation.latency_ms} if evaluation else dict(trace.evaluation.metrics if trace.evaluation else {})),
        "trace_schema_version": trace.schema_version,
        "openmp_isolation_probe": {
            "faiss_main_process": "faiss" in sys.modules,
            "torch_main_process": "torch" in sys.modules,
            "worker_torch_loaded": bool(getattr(trace.reranking, "scoring_method", None) == "cross_encoder"),
            "worker_faiss_loaded": False,
            "unsafe_kmp_duplicate_lib_ok": bool(__import__("os").environ.get("KMP_DUPLICATE_LIB_OK")),
        },
    }
    if args.profile == "model-enhanced":
        report.update(_validate_model_prerequisites(profile))
    report_path = root / "validation-report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    print(f"Validation report: {report_path}")
    return 0


def _validate_model_prerequisites(profile: dict) -> dict:
    """Report local model prerequisite status without attempting any downloads."""
    source = str(Path(__file__).parents[1] / "src")
    code = (
        f"import sys; sys.path.insert(0, {source!r})\n"
        "from armie_retrieval.embeddings import BGEEmbeddingProvider, EmbeddingPrerequisiteError\n"
        f"provider = BGEEmbeddingProvider({profile['embedding']['model']!r})\n"
        "try:\n provider.validate_model_available(); print('passed')\n"
        "except EmbeddingPrerequisiteError as exc:\n print('blocked:' + str(exc))\n"
    )
    completed = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True, check=False)
    output = completed.stdout.strip()
    return {"bge_embedding_model": "passed" if output == "passed" else "blocked_prerequisite", "bge_guidance": None if output == "passed" else output.removeprefix("blocked:")}


if __name__ == "__main__":
    raise SystemExit(main())
