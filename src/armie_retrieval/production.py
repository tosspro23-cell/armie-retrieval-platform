"""Production component composition without changing the runtime architecture."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from armie_retrieval.embeddings import EmbeddingProvider
from armie_retrieval.indexing import KeywordIndex
from armie_retrieval.processors import DeduplicateProcessor, ExpertRerankProcessor, MetadataFilterProcessor, QueryAwareRerankProcessor
from armie_retrieval.rerankers import MetadataBoostReranker, RerankerProvider
from armie_retrieval.providers import NetworkXKnowledgeGraphProvider
from armie_retrieval.registries import ProcessorRegistry, ProviderRegistry, RetrieverRegistry
from armie_retrieval.retrievers import FaissDenseRetriever, GraphRetriever, HybridRetriever, IndexedSparseRetriever
from armie_retrieval.runtime import RetrievalRuntime
from armie_retrieval.vectorstores import FaissVectorStore


@dataclass(frozen=True)
class ProductionArtifacts:
    root: Path

    @property
    def vector(self) -> Path:
        return self.root / "vector"

    @property
    def keyword(self) -> Path:
        return self.root / "keyword"

    @property
    def graph(self) -> Path:
        return self.root / "graph"


@dataclass(frozen=True)
class ProductionPlatform:
    runtime: RetrievalRuntime
    retrievers: RetrieverRegistry
    processors: ProcessorRegistry
    providers: ProviderRegistry


def create_production_platform(
    artifacts: ProductionArtifacts, embedding_provider: EmbeddingProvider, *, reranker: RerankerProvider | None = None,
) -> ProductionPlatform:
    """Load prebuilt artifacts and register executable production components."""
    vector_store = FaissVectorStore(artifacts.vector)
    keyword_index = KeywordIndex(artifacts.keyword)
    graph_provider = NetworkXKnowledgeGraphProvider.from_artifact(artifacts.graph)

    dense = FaissDenseRetriever(vector_store, embedding_provider)
    sparse = IndexedSparseRetriever(keyword_index)
    graph = GraphRetriever(graph_provider)

    retrievers = RetrieverRegistry()
    retrievers.register("faiss_dense", dense, capabilities={"dense"}, version="0.2.3", priority=100)
    retrievers.register("indexed_sparse", sparse, capabilities={"sparse"}, version="0.2.3", priority=100)
    retrievers.register("hybrid", HybridRetriever(dense, sparse), capabilities={"hybrid"}, version="0.2.3", priority=100)
    retrievers.register("networkx_graph", graph, capabilities={"graph"}, version="0.2.3", priority=100)

    processors = ProcessorRegistry()
    for processor in (
        DeduplicateProcessor(), MetadataFilterProcessor(), ExpertRerankProcessor(),
        QueryAwareRerankProcessor(reranker or MetadataBoostReranker(), name="rerank"),
    ):
        processors.register(processor.name, processor, capabilities={processor.name}, version="0.2.3", priority=100)

    providers = ProviderRegistry()
    # Index artifacts are deliberately not registry entries. They are loaded by
    # retrievers as offline-built assets. The graph provider remains executable.
    providers.register("networkx_graph", graph_provider, capabilities={"graph"}, version="0.2.3", priority=100)
    return ProductionPlatform(RetrievalRuntime(retrievers, processors), retrievers, processors, providers)
