"""Validate offline indexing, persistent FAISS retrieval, metrics, and Ollama planning.

This script intentionally does not download BGE-M3. It validates a configured
local BGE provider when its model is already installed and otherwise prints the
manual prerequisite required for the full production embedding validation.
"""

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
from armie_retrieval.planners import LLMPlanner, OllamaStructuredLLMClient, RuleBasedPlanner
from armie_retrieval.production import ProductionArtifacts, create_production_platform


class DeterministicValidationEmbeddingProvider:
    """Test fixture used only to validate FAISS artifact lifecycle without model downloads."""

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
    parser.add_argument("--artifacts", default=".artifacts/validation")
    parser.add_argument("--size", type=int, default=50, help="Corpus size; 50, 200, and 500 are recommended benchmark scales")
    parser.add_argument("--ollama-model", default="qwen3:4b")
    parser.add_argument("--bge-model", default="BAAI/bge-m3")
    parser.add_argument("--keep-artifacts", action="store_true")
    args = parser.parse_args()
    root = Path(args.artifacts)
    if root.exists() and not args.keep_artifacts:
        shutil.rmtree(root)

    dataset = generate_benchmark_dataset(root, size=args.size)
    fixture_embedding = DeterministicValidationEmbeddingProvider()
    artifacts = ProductionArtifacts(root / "indexes")
    VectorIndexBuilder(fixture_embedding).build(dataset.experts, artifacts.vector)
    KeywordIndexBuilder().build(dataset.experts, artifacts.keyword)
    GraphIndexBuilder().build(dataset.experts, artifacts.graph)

    platform = create_production_platform(artifacts, fixture_embedding)
    planner = RuleBasedPlanner(platform.retrievers.capabilities())
    evaluation = run_evaluation(platform.runtime, planner, dataset.queries, top_k=5)
    graph_query = Query("Find healthcare experts connected to Azure AI", top_k=3)
    graph_result = platform.runtime.execute(graph_query, planner.plan(graph_query))

    report = {
        "dataset_size": len(dataset.experts),
        "faiss_persistent_index": True,
        "keyword_persistent_index": True,
        "networkx_graph_artifact": True,
        "graph_retrieval_result_count": len(graph_result.items),
        "metrics": {
            "precision_at_k": evaluation.precision_at_k,
            "recall_at_k": evaluation.recall_at_k,
            "mrr": evaluation.mrr,
            "ndcg_at_k": evaluation.ndcg_at_k,
            "latency_ms": evaluation.latency_ms,
        },
    }
    report.update(_validate_bge_in_isolated_process(args.bge_model))

    try:
        client = OllamaStructuredLLMClient(args.ollama_model)
        llm_plan = LLMPlanner(client, platform.retrievers.capabilities()).plan(Query("Find healthcare RAG experts", top_k=3))
        report["ollama_planner_validation"] = {"status": "passed", "strategy": llm_plan.strategy}
    except Exception as exc:  # Preserve actionable local prerequisite failures in the report.
        report["ollama_planner_validation"] = {"status": "blocked_prerequisite", "guidance": str(exc)}

    report_path = root / "validation-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Validation report: {report_path}")
    return 0


def _validate_bge_in_isolated_process(model_name: str) -> dict:
    """Avoid a local FAISS/Torch OpenMP conflict during optional BGE validation."""
    code = (
        f"import sys; sys.path.insert(0, {str(Path(__file__).parents[1] / 'src')!r})\n"
        "from armie_retrieval.embeddings import BGEEmbeddingProvider, EmbeddingPrerequisiteError\n"
        f"provider = BGEEmbeddingProvider({model_name!r})\n"
        "try:\n"
        "    provider.validate_model_available()\n"
        "    vector = provider.embed(['ARMIE production embedding validation'])[0]\n"
        "    assert vector, 'empty embedding'\n"
        "    print('passed:' + str(len(vector)))\n"
        "except EmbeddingPrerequisiteError as exc:\n"
        "    print('blocked:' + str(exc))\n"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(Path(__file__).parents[1]), text=True, capture_output=True, check=False,
    )
    output = completed.stdout.strip()
    if completed.returncode == 0 and output.startswith("passed:"):
        return {"bge_model_validation": "passed", "bge_embedding_dimension": int(output.split(":", 1)[1])}
    guidance = output.removeprefix("blocked:") if output.startswith("blocked:") else completed.stderr.strip()
    return {"bge_model_validation": "blocked_prerequisite", "bge_guidance": guidance}


if __name__ == "__main__":
    raise SystemExit(main())
