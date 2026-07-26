"""Configuration-led embedding selection behind the stable provider contract."""

from __future__ import annotations

from typing import Any, Mapping

from .bge import BGEEmbeddingProvider


def create_embedding_provider(config: Mapping[str, Any]):
    """Construct an embedding provider without exposing it to a retrieval plan."""
    settings = config.get("embedding", {})
    provider_type = settings.get("provider", "bge")
    if provider_type != "bge":
        raise ValueError(f"Unsupported embedding provider type: {provider_type}")
    return BGEEmbeddingProvider(
        model_name=settings.get("model", "BAAI/bge-m3"),
        device=settings.get("device"),
        local_files_only=bool(settings.get("local_files_only", True)),
    )
