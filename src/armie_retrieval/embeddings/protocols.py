"""Stable embedding-provider boundary for offline builders and online retrievers."""

from __future__ import annotations

from typing import Protocol, Sequence


class EmbeddingProvider(Protocol):
    @property
    def dimension(self) -> int:
        """Return output vector dimensionality."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed inputs without building or mutating an index."""
