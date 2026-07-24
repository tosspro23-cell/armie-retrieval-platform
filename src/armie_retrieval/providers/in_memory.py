"""Provider boundary for the portable MVP knowledge source."""

from __future__ import annotations

from typing import Iterable

from armie_retrieval.models.domain import ResultItem


class InMemoryKnowledgeProvider:
    """A replaceable source adapter; retrievers never own the data source."""

    name = "in_memory"
    capabilities = frozenset({"dense", "sparse", "metadata_filter"})

    def __init__(self, items: Iterable[ResultItem]) -> None:
        self._items = tuple(items)

    def items(self) -> tuple[ResultItem, ...]:
        return self._items
