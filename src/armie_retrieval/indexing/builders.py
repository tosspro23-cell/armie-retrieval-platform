"""Offline index builders. Runtime retrievers consume their artifacts only."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Iterable

from armie_retrieval.embeddings import EmbeddingProvider
from armie_retrieval.models import ResultItem
from armie_retrieval.providers import NetworkXKnowledgeGraphProvider

from .keyword_index import KeywordIndex
from .serializers import result_item_to_dict, searchable_text


class VectorIndexBuilder:
    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self._embedding_provider = embedding_provider

    def build(self, items: Iterable[ResultItem], artifact_directory: str | Path) -> Path:
        materialized = list(items)
        if not materialized:
            raise ValueError("Cannot build a vector index with no knowledge items")
        try:
            import faiss
            import numpy as np
        except ImportError as exc:
            raise RuntimeError("FAISS and NumPy are required. Install project dependencies with `python3 -m pip install .`.") from exc
        vectors = self._embedding_provider.embed([searchable_text(item) for item in materialized])
        matrix = np.asarray(vectors, dtype="float32")
        if matrix.ndim != 2 or matrix.shape[0] != len(materialized):
            raise ValueError("Embedding provider returned an invalid vector matrix")
        faiss.normalize_L2(matrix)
        directory = Path(artifact_directory)
        directory.mkdir(parents=True, exist_ok=True)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        faiss.write_index(index, str(directory / "index.faiss"))
        (directory / "items.json").write_text(
            json.dumps([result_item_to_dict(item) for item in materialized], indent=2), encoding="utf-8"
        )
        return directory


class KeywordIndexBuilder:
    def build(self, items: Iterable[ResultItem], artifact_directory: str | Path) -> Path:
        materialized = list(items)
        KeywordIndex.build(materialized, artifact_directory)
        return Path(artifact_directory)


class GraphIndexBuilder:
    """Persist the existing NetworkX graph representation as an offline artifact."""

    GRAPH_FILE = "graph.pkl"
    ITEMS_FILE = "experts.json"

    def build(self, items: Iterable[ResultItem], artifact_directory: str | Path) -> Path:
        materialized = list(items)
        provider = NetworkXKnowledgeGraphProvider.from_experts(materialized)
        directory = Path(artifact_directory)
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / self.GRAPH_FILE).open("wb") as handle:
            pickle.dump(provider.graph, handle)
        (directory / self.ITEMS_FILE).write_text(
            json.dumps([result_item_to_dict(item) for item in materialized], indent=2), encoding="utf-8"
        )
        return directory
