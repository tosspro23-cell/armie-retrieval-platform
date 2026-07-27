"""Run from repository root: python3 examples/expert_discovery_demo.py.

The two LLM examples use a deterministic StructuredLLMClient fixture so this repository
can be run without credentials. Replace it with an API-backed client in deployment; no
runtime component needs to change.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval import ExecutionObservation, Query, ResultItem, RetrievalRuntime
from armie_retrieval.evaluation import evaluate
from armie_retrieval.learning import LearningEngine, ObservationStore, PolicyRepository
from armie_retrieval.planners import create_planner
from armie_retrieval.processors import DeduplicateProcessor, ExpertRerankProcessor, MetadataFilterProcessor
from armie_retrieval.providers import InMemoryKnowledgeProvider, NetworkXKnowledgeGraphProvider
from armie_retrieval.registries import ProcessorRegistry, ProviderRegistry, RetrieverRegistry
from armie_retrieval.retrievers import DenseRetriever, GraphRetriever, HybridRetriever, SparseRetriever


EXPERTS = (
    ResultItem("expert_ada", "expert", "Ada Chen", "Built production RAG systems and Azure AI search for hospital networks.", {"industry": "healthcare", "country": "Portugal", "skills": "Azure AI, RAG, retrieval", "technology": "Azure AI Search", "organization": "Hospital Network", "projects": "Clinical Knowledge Platform"}),
    ResultItem("expert_ben", "expert", "Ben Torres", "Leads machine-learning platforms for oncology data and healthcare analytics.", {"industry": "healthcare", "country": "UK", "skills": "MLOps, oncology, ML platform", "technology": "Python", "organization": "NHS", "projects": "Oncology Data Platform"}),
    ResultItem("expert_carla", "expert", "Carla Silva", "Former search engineer specialising in semantic retrieval, ranking and expert networks.", {"industry": "professional_services", "country": "Portugal", "skills": "semantic search, ranking, knowledge graph", "technology": "NetworkX", "organization": "Expert Network", "projects": "Knowledge Discovery"}),
    ResultItem("expert_dan", "expert", "Dan Price", "Product leader for fintech recommendation systems and data products.", {"industry": "fintech", "country": "UK", "skills": "recommendation, product", "technology": "SQL", "organization": "Fintech", "projects": "Recommendation Platform"}),
)


class DemoStructuredLLM:
    """A deterministic test double for a structured LLM response."""

    def complete(self, *, prompt: str) -> Mapping[str, Any]:
        if "network" in prompt.lower() or "connected" in prompt.lower():
            return {"strategy": "graph", "processors": ["deduplicate", "expert_rerank"], "top_k": 2}
        return {"strategy": "dense", "processors": ["deduplicate", "expert_rerank"], "top_k": 2}


def build_runtime() -> tuple[RetrievalRuntime, frozenset[str], ProviderRegistry]:
    provider = InMemoryKnowledgeProvider(EXPERTS)
    dense, sparse = DenseRetriever(provider), SparseRetriever(provider)
    retrievers = RetrieverRegistry()
    retrievers.register("dense", dense, capabilities={"dense"}, version="0.2.3", priority=80)
    retrievers.register("sparse", sparse, capabilities={"sparse"}, version="0.2.3", priority=70)
    retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"}, version="0.2.3", priority=100)
    providers = ProviderRegistry()
    providers.register("in_memory", provider, capabilities=provider.capabilities, version="0.2.3", priority=100)
    try:
        graph_provider = NetworkXKnowledgeGraphProvider.from_experts(EXPERTS)
        graph = GraphRetriever(graph_provider)
        retrievers.register("graph", graph, capabilities={"graph"}, version="0.2.3", priority=90)
        providers.register("networkx_graph", graph_provider, capabilities=graph_provider.capabilities, version="0.2.3", priority=90)
    except RuntimeError as error:
        print(f"Graph capability unavailable: {error}")
    processors = ProcessorRegistry()
    for processor in (DeduplicateProcessor(), MetadataFilterProcessor(), ExpertRerankProcessor()):
        processors.register(processor.name, processor, capabilities={processor.name}, version="0.2.3")
    return RetrievalRuntime(retrievers, processors), retrievers.capabilities(), providers


def demonstrate(label: str, planner_config: Mapping[str, Any], query: Query, runtime: RetrievalRuntime, capabilities: frozenset[str]) -> None:
    planner = create_planner(planner_config, available_capabilities=capabilities, llm_client=DemoStructuredLLM())
    plan = planner.plan(query)
    result = runtime.execute(query, plan)
    print(f"\n{label}\nPlan: strategy={plan.strategy}; processors={', '.join(plan.processor_names)}")
    for rank, item in enumerate(result.items, 1):
        print(f"{rank}. {item.title} — {item.score:.3f} — {item.metadata['country']}")
    metrics = evaluate(result, {"expert_ada", "expert_ben"}, k=2)
    print(f"Precision@2={metrics.precision_at_k:.2f}; Recall@2={metrics.recall_at_k:.2f}; MRR={metrics.reciprocal_rank:.2f}; latency={metrics.latency_ms:.2f}ms")


def main() -> None:
    runtime, capabilities, _providers = build_runtime()
    demonstrate("Rule Planner → Hybrid Retrieval", {"planner": {"type": "rule"}}, Query("Find experts for production Azure AI retrieval in healthcare", filters={"industry": "healthcare"}, top_k=2), runtime, capabilities)
    demonstrate("LLM Planner → Dense Retrieval", {"planner": {"type": "llm"}}, Query("Find experts in semantic retrieval", top_k=2), runtime, capabilities)
    if "graph" in capabilities:
        demonstrate("LLM Planner → Graph Retrieval", {"planner": {"type": "llm"}}, Query("Find experts connected to the healthcare network", top_k=2), runtime, capabilities)
    else:
        print("\nLLM Planner → Graph Retrieval is available after installing NetworkX.")

    # Offline learning: observations become policy; the runtime never reads this store.
    observations, policies = ObservationStore(), PolicyRepository()
    observations.append(ExecutionObservation("processor", "llm_judge", "unsupported_capability", {"processor": "llm_judge"}))
    policy = LearningEngine().optimize_and_publish(observations, policies)
    print(f"\nOffline policy published: v{policy.version}; rationale={'; '.join(policy.rationale) or 'no changes'}")


if __name__ == "__main__":
    main()
