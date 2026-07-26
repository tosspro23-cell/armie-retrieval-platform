"""Persistent keyword index artifact consumed by the production sparse retriever."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from armie_retrieval.models import ResultItem

from .serializers import result_item_to_dict, searchable_text

TOKEN = re.compile(r"[a-z0-9]+")


class KeywordIndex:
    FILE_NAME = "keyword_index.json"

    def __init__(self, artifact_directory: str | Path) -> None:
        self._directory = Path(artifact_directory)
        self._items: dict[str, ResultItem] | None = None
        self._term_frequencies: dict[str, Counter[str]] | None = None

    @classmethod
    def build(cls, items: list[ResultItem], artifact_directory: str | Path) -> None:
        directory = Path(artifact_directory)
        directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "items": [result_item_to_dict(item) for item in items],
            "term_frequencies": {
                item.id: dict(Counter(TOKEN.findall(searchable_text(item).lower()))) for item in items
            },
        }
        (directory / cls.FILE_NAME).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> None:
        path = self._directory / self.FILE_NAME
        if not path.exists():
            raise FileNotFoundError(f"Keyword index artifact is missing at {path}. Run the offline KeywordIndexBuilder first.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._items = {entry["id"]: ResultItem(**entry) for entry in payload["items"]}
        self._term_frequencies = {item_id: Counter(counts) for item_id, counts in payload["term_frequencies"].items()}

    def search(self, query: str, top_k: int) -> list[tuple[ResultItem, float]]:
        if self._items is None or self._term_frequencies is None:
            self.load()
        query_terms = Counter(TOKEN.findall(query.lower()))
        scored = []
        for item_id, terms in self._term_frequencies.items():
            score = sum(min(count, terms[term]) for term, count in query_terms.items())
            if score:
                scored.append((self._items[item_id], float(score)))
        return sorted(scored, key=lambda pair: pair[1], reverse=True)[:top_k]
