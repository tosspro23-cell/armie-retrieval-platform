"""NetworkX-backed graph provider for validating the graph-retrieval contract."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Iterable

from armie_retrieval.models import ResultItem

try:  # Import is optional only because the execution environment may not ship NetworkX.
    import networkx as nx
except ImportError:  # pragma: no cover - exercised by runtime dependency guard
    nx = None


class NetworkXKnowledgeGraphProvider:
    name = "networkx_graph"
    capabilities = frozenset({"graph"})

    def __init__(self) -> None:
        if nx is None:
            raise RuntimeError("NetworkX is required for graph retrieval. Install project dependencies before using this provider.")
        self.graph = nx.MultiDiGraph()
        self._experts: dict[str, ResultItem] = {}

    @classmethod
    def from_experts(cls, experts: Iterable[ResultItem]) -> "NetworkXKnowledgeGraphProvider":
        provider = cls()
        for expert in experts:
            provider.add_expert(expert)
        return provider

    def add_expert(self, expert: ResultItem) -> None:
        self._experts[expert.id] = expert
        self.graph.add_node(expert.id, label=expert.title, node_type="Person")
        relationships = {
            "Skill": str(expert.metadata.get("skills", "")).split(","),
            "Organization": [str(expert.metadata.get("organization", ""))],
            "Domain": [str(expert.metadata.get("industry", ""))],
            "Project": str(expert.metadata.get("projects", "")).split(","),
            "Technology": str(expert.metadata.get("technology", "")).split(","),
        }
        for node_type, values in relationships.items():
            for value in (value.strip() for value in values):
                if not value:
                    continue
                node_id = f"{node_type.lower()}:{value.lower()}"
                self.graph.add_node(node_id, label=value, node_type=node_type)
                self.graph.add_edge(expert.id, node_id, relation=f"HAS_{node_type.upper()}")
                self.graph.add_edge(node_id, expert.id, relation=f"HAS_{node_type.upper()}")

    def expert_items(self) -> dict[str, ResultItem]:
        return self._experts

    @classmethod
    def from_artifact(cls, artifact_directory: str | Path) -> "NetworkXKnowledgeGraphProvider":
        """Load an offline graph artifact; runtime never rebuilds it."""
        directory = Path(artifact_directory)
        graph_path = directory / "graph.pkl"
        items_path = directory / "experts.json"
        if not graph_path.exists() or not items_path.exists():
            raise FileNotFoundError(
                f"Graph index artifacts are missing in {directory}. Run the offline GraphIndexBuilder first."
            )
        provider = cls()
        with graph_path.open("rb") as handle:
            provider.graph = pickle.load(handle)
        provider._experts = {
            entry["id"]: ResultItem(**entry) for entry in json.loads(items_path.read_text(encoding="utf-8"))
        }
        return provider
