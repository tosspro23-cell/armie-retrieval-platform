"""Persistent FAISS index artifact consumer; it never builds an index at query time."""

from __future__ import annotations

import json
from pathlib import Path

from armie_retrieval.models import ResultItem


class FaissVectorStoreError(RuntimeError):
    pass


class FaissVectorStore:
    INDEX_FILE = "index.faiss"
    ITEMS_FILE = "items.json"

    def __init__(self, artifact_directory: str | Path) -> None:
        self._directory = Path(artifact_directory)
        self._index = None
        self._items: tuple[ResultItem, ...] | None = None

    def load(self) -> None:
        index_path = self._directory / self.INDEX_FILE
        items_path = self._directory / self.ITEMS_FILE
        if not index_path.exists() or not items_path.exists():
            raise FaissVectorStoreError(
                f"Persistent vector index artifacts are missing in {self._directory}. Run the offline VectorIndexBuilder first."
            )
        try:
            import faiss
        except ImportError as exc:
            raise FaissVectorStoreError("FAISS is required. Install project dependencies with `python3 -m pip install .`.") from exc
        self._index = faiss.read_index(str(index_path))
        raw_items = json.loads(items_path.read_text(encoding="utf-8"))
        self._items = tuple(ResultItem(**item) for item in raw_items)

    def search(self, vector: list[float], top_k: int) -> list[tuple[ResultItem, float]]:
        if self._index is None or self._items is None:
            self.load()
        try:
            import numpy as np
        except ImportError as exc:
            raise FaissVectorStoreError("NumPy is required. Install project dependencies with `python3 -m pip install .`.") from exc
        scores, positions = self._index.search(np.asarray([vector], dtype="float32"), top_k)
        return [
            (self._items[position], float(score))
            for score, position in zip(scores[0], positions[0])
            if position >= 0
        ]
