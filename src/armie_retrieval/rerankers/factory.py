"""Explicit reranker selection with controlled deterministic fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .providers import BGECrossEncoderReranker, ControlledFallbackReranker, MetadataBoostReranker, NoOpReranker, RerankerPrerequisiteError


@dataclass(frozen=True)
class RerankerSelection:
    provider: object
    requested: str
    actual: str
    requested_model: str | None
    fallback_enabled: bool
    fallback_reason: str | None = None


def create_reranker(config: Mapping[str, Any]) -> RerankerSelection:
    requested = str(config.get("type", "metadata_boost"))
    aliases = {"metadata": "metadata_boost", "bge": "bge_cross_encoder", "none": "none"}
    requested = aliases.get(requested, requested)
    model = config.get("model")
    fallback = aliases.get(str(config.get("fallback", "none")), str(config.get("fallback", "none")))
    if requested == "none":
        return RerankerSelection(NoOpReranker(), requested, "none", model, False)
    if requested == "metadata_boost":
        return RerankerSelection(MetadataBoostReranker(), requested, "metadata_boost", model, False)
    if requested != "bge_cross_encoder":
        raise ValueError(f"Unsupported reranker provider: {requested}")
    provider = BGECrossEncoderReranker(
        str(model or "BAAI/bge-reranker-v2-m3"),
        device=str(config.get("device", "auto")), batch_size=int(config.get("batch_size", 8)),
        isolated=bool(config.get("isolated", False)), timeout_seconds=float(config.get("timeout_seconds", 120)),
    )
    try:
        provider.validate_model_available()
        fallback_provider = MetadataBoostReranker() if fallback == "metadata_boost" else (NoOpReranker() if fallback == "none" else None)
        wrapped = ControlledFallbackReranker(provider, fallback_provider) if fallback_provider and fallback != "none" else provider
        return RerankerSelection(wrapped, requested, requested, provider.model_name, fallback != "none")
    except RerankerPrerequisiteError as exc:
        if fallback == "metadata_boost":
            return RerankerSelection(MetadataBoostReranker(), requested, "metadata_boost", provider.model_name, True, str(exc))
        if fallback == "none":
            return RerankerSelection(NoOpReranker(), requested, "none", provider.model_name, True, str(exc))
        raise
