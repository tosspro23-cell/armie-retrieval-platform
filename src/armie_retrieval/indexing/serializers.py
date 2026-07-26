"""Artifact serializers shared only by offline index builders and stores."""

from __future__ import annotations

from armie_retrieval.models import ResultItem


def result_item_to_dict(item: ResultItem) -> dict:
    return {
        "id": item.id,
        "object_type": item.object_type,
        "title": item.title,
        "content": item.content,
        "metadata": dict(item.metadata),
        "score": item.score,
        "sources": list(item.sources),
        "signals": dict(item.signals),
    }


def searchable_text(item: ResultItem) -> str:
    return " ".join([item.title, item.content, *map(str, item.metadata.values())])
