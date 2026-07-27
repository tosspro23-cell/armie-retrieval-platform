"""Bounded, replaceable reranker providers for retrieval result candidates."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from dataclasses import dataclass
from typing import Mapping, Protocol

from armie_retrieval.models import Query, ResultItem


class RerankerPrerequisiteError(RuntimeError):
    """Raised when a locally configured reranker model is unavailable."""


class IsolatedRerankerError(RerankerPrerequisiteError):
    """A controlled failure returned by the isolated reranker process."""

    def __init__(self, message: str, diagnostic: Mapping[str, object]) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic


@dataclass(frozen=True)
class RerankItem:
    item: ResultItem
    raw_relevance_score: float
    input_rank: int
    output_rank: int
    document: str | None = None


@dataclass(frozen=True)
class RerankResult:
    items: tuple[RerankItem, ...]
    provider: str
    model: str | None = None
    model_available: bool = True
    device: str | None = None
    batch_size: int | None = None
    model_load_latency_ms: float = 0.0
    inference_latency_ms: float = 0.0
    warnings: tuple[str, ...] = ()
    scored_items: tuple[RerankItem, ...] = ()
    scoring_method: str = "none"
    fallback_diagnostic: Mapping[str, object] | None = None


class RerankerProvider(Protocol):
    name: str

    def rerank(self, query: Query, candidates: tuple[ResultItem, ...], top_k: int) -> RerankResult:
        """Score a bounded candidate pool and return ordered candidates."""


class ExpertRerankDocumentBuilder:
    """Stable expert serialization for query-candidate cross-encoder scoring."""

    DEFAULT_FIELDS = ("industry", "skills", "technology", "organization", "projects", "experience", "country", "description")

    def __init__(self, *, fields: tuple[str, ...] = DEFAULT_FIELDS, max_length: int = 1800) -> None:
        self.fields = fields
        self.max_length = max_length

    def build(self, item: ResultItem) -> str:
        lines = [f"Expert: {item.title}"]
        for field in self.fields:
            value = item.content if field == "description" else item.metadata.get(field)
            if value not in (None, "", (), [], {}):
                rendered = ", ".join(map(str, value)) if isinstance(value, (tuple, list, set)) else str(value)
                lines.append(f"{field.replace('_', ' ').title()}: {rendered}")
        return "\n".join(lines)[: self.max_length]


class NoOpReranker:
    name = "none"

    def rerank(self, query: Query, candidates: tuple[ResultItem, ...], top_k: int) -> RerankResult:
        selected = candidates[:top_k]
        all_items = tuple(RerankItem(item, item.score, rank, rank) for rank, item in enumerate(candidates, 1))
        return RerankResult(all_items[:top_k], provider=self.name, scored_items=all_items, scoring_method="none")


class MetadataBoostReranker:
    """Deterministic rules reranker; it is not a neural semantic model."""

    name = "metadata_boost"

    def rerank(self, query: Query, candidates: tuple[ResultItem, ...], top_k: int) -> RerankResult:
        scored: list[tuple[ResultItem, float, int]] = []
        for rank, item in enumerate(candidates, 1):
            boost = sum(
                0.05 for key, value in query.filters.items()
                if str(item.metadata.get(key, "")).lower() == str(value).lower()
            )
            scored.append((item, item.score + boost, rank))
        scored.sort(key=lambda row: row[1], reverse=True)
        all_items = tuple(RerankItem(item, score, input_rank, output_rank) for output_rank, (item, score, input_rank) in enumerate(scored, 1))
        return RerankResult(all_items[:top_k], provider=self.name, scored_items=all_items, scoring_method="metadata_boost")


class BGECrossEncoderReranker:
    """Local BGE cross-encoder; weights must already be available locally."""

    name = "bge_cross_encoder"

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        *,
        device: str = "auto",
        batch_size: int = 8,
        document_builder: ExpertRerankDocumentBuilder | None = None,
        local_files_only: bool = True,
        model=None,
        isolated: bool = False,
        timeout_seconds: float = 120.0,
        runner=None,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self._builder = document_builder or ExpertRerankDocumentBuilder()
        self._local_files_only = local_files_only
        self._model = model
        self._load_latency_ms = 0.0
        self.isolated = isolated
        self.timeout_seconds = timeout_seconds
        self._runner = runner or subprocess.run

    def validate_model_available(self) -> None:
        if self.isolated:
            # A lightweight empty request verifies that the executable worker can
            # import the model without importing Torch in this parent process.
            self._invoke_worker("", (), validate_only=True)
            return
        self._ensure_model()

    def rerank(self, query: Query, candidates: tuple[ResultItem, ...], top_k: int) -> RerankResult:
        if not candidates:
            return RerankResult((), self.name, self.model_name, device=self._resolved_device(), batch_size=self.batch_size, scored_items=())
        if self.isolated:
            return self._rerank_isolated(query, candidates, top_k)
        documents = [self._builder.build(item) for item in candidates]
        model = self._ensure_model()
        started = time.perf_counter()
        try:
            scores = model.predict([(query.text, document) for document in documents], batch_size=self.batch_size, show_progress_bar=False)
        except TypeError:  # lightweight mocks and older SentenceTransformers APIs
            scores = model.predict([(query.text, document) for document in documents], batch_size=self.batch_size)
        inference_ms = (time.perf_counter() - started) * 1000
        rows = [(item, float(score), rank, document) for rank, (item, score, document) in enumerate(zip(candidates, scores, documents), 1)]
        rows.sort(key=lambda row: row[1], reverse=True)
        all_items = tuple(RerankItem(item, score, input_rank, output_rank, document) for output_rank, (item, score, input_rank, document) in enumerate(rows, 1))
        return RerankResult(
            all_items[:top_k],
            provider=self.name,
            model=self.model_name,
            device=self._resolved_device(),
            batch_size=self.batch_size,
            model_load_latency_ms=self._load_latency_ms,
            inference_latency_ms=inference_ms,
            scored_items=all_items,
            scoring_method="cross_encoder",
        )

    def _rerank_isolated(self, query: Query, candidates: tuple[ResultItem, ...], top_k: int) -> RerankResult:
        response = self._invoke_worker(query.text, candidates)
        scores = {row["id"]: float(row["raw_relevance_score"]) for row in response["scores"]}
        documents = {item.id: self._builder.build(item) for item in candidates}
        rows = [(item, scores[item.id], rank, documents[item.id]) for rank, item in enumerate(candidates, 1)]
        rows.sort(key=lambda row: row[1], reverse=True)
        all_items = tuple(RerankItem(item, score, input_rank, output_rank, document) for output_rank, (item, score, input_rank, document) in enumerate(rows, 1))
        return RerankResult(
            all_items[:top_k], provider=self.name, model=self.model_name, device=str(response["actual_device"]), batch_size=self.batch_size,
            model_load_latency_ms=float(response["model_load_latency_ms"]), inference_latency_ms=float(response["inference_latency_ms"]),
            warnings=tuple(response.get("warnings", ())), scored_items=all_items, scoring_method="cross_encoder",
        )

    def _invoke_worker(self, query: str, candidates: tuple[ResultItem, ...], *, validate_only: bool = False) -> Mapping[str, object]:
        request_id = str(uuid.uuid4())
        payload = {
            "request_id": request_id, "model": self.model_name, "device": self.device, "batch_size": self.batch_size,
            "query": query, "candidates": [] if validate_only else [{"id": item.id, "document": self._builder.build(item)} for item in candidates],
        }
        try:
            source_root = str(Path(__file__).resolve().parents[2])
            environment = dict(os.environ)
            environment["PYTHONPATH"] = source_root + os.pathsep + environment.get("PYTHONPATH", "")
            completed = self._runner([sys.executable, "-m", "armie_retrieval.rerankers.worker"], input=json.dumps(payload), text=True, capture_output=True, timeout=self.timeout_seconds, check=False, env=environment)
        except subprocess.TimeoutExpired as exc:
            raise IsolatedRerankerError("Isolated cross-encoder timed out.", {"fallback_type": "isolated_reranker_failure", "timeout": True, "error_type": "timeout", "stderr": str(getattr(exc, "stderr", "") or ""), "requested_model": self.model_name}) from exc
        stdout, stderr = completed.stdout or "", completed.stderr or ""
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise IsolatedRerankerError("Isolated cross-encoder returned malformed JSON.", {"fallback_type": "isolated_reranker_failure", "exit_code": completed.returncode, "error_type": "malformed_json", "stderr": stderr[:1000], "requested_model": self.model_name}) from exc
        diagnostic = {"fallback_type": "isolated_reranker_failure", "exit_code": completed.returncode, "timeout": False, "error_type": response.get("error_type"), "stderr": stderr[:1000], "requested_model": self.model_name}
        if completed.returncode != 0 or response.get("status") != "ok":
            raise IsolatedRerankerError(str(response.get("message", "Isolated cross-encoder failed.")), diagnostic)
        if response.get("request_id") != request_id:
            raise IsolatedRerankerError("Isolated cross-encoder response ID did not match the request.", diagnostic | {"error_type": "request_id_mismatch"})
        scores = response.get("scores")
        expected_ids = [item.id for item in candidates]
        if not isinstance(scores, list) or len(scores) != len(expected_ids):
            raise IsolatedRerankerError("Isolated cross-encoder returned an incomplete score set.", diagnostic | {"error_type": "score_count_mismatch"})
        returned_ids = [row.get("id") for row in scores if isinstance(row, dict)]
        if len(returned_ids) != len(scores) or len(set(returned_ids)) != len(returned_ids) or set(returned_ids) != set(expected_ids):
            raise IsolatedRerankerError("Isolated cross-encoder returned duplicate or missing candidate IDs.", diagnostic | {"error_type": "candidate_id_mismatch"})
        for row in scores:
            try:
                if not math.isfinite(float(row["raw_relevance_score"])):
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                raise IsolatedRerankerError("Isolated cross-encoder returned a non-finite score.", diagnostic | {"error_type": "invalid_score"})
        return response

    def _resolved_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch
            if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
        return "cpu"

    def _ensure_model(self):
        if self._model is not None:
            return self._model
        started = time.perf_counter()
        try:
            from sentence_transformers import CrossEncoder
            device = self._resolved_device()
            try:
                self._model = CrossEncoder(self.model_name, device=device, local_files_only=self._local_files_only)
            except TypeError:
                self._model = CrossEncoder(self.model_name, device=device)
            self._load_latency_ms = (time.perf_counter() - started) * 1000
            return self._model
        except ImportError as exc:
            raise RerankerPrerequisiteError("sentence-transformers is required. Install project model dependencies first.") from exc
        except Exception as exc:
            raise RerankerPrerequisiteError(
                f"Reranker model {self.model_name!r} is not available locally. Download it explicitly, for example: "
                f"`huggingface-cli download {self.model_name}`."
            ) from exc


class ControlledFallbackReranker:
    """Keep runtime fallback inside the provider boundary without changing plans."""

    def __init__(self, primary: RerankerProvider, fallback: RerankerProvider | None) -> None:
        self.primary = primary
        self.fallback = fallback
        self.name = getattr(primary, "name", "reranker")

    def rerank(self, query: Query, candidates: tuple[ResultItem, ...], top_k: int) -> RerankResult:
        try:
            return self.primary.rerank(query, candidates, top_k)
        except IsolatedRerankerError as exc:
            if self.fallback is None:
                raise
            result = self.fallback.rerank(query, candidates, top_k)
            diagnostic = dict(exc.diagnostic)
            diagnostic.update({"fallback_provider": result.provider, "fallback_reason": str(exc), "actual_provider": result.provider})
            return RerankResult(
                result.items, provider=result.provider, model=result.model, model_available=result.model_available,
                device=result.device, batch_size=result.batch_size, model_load_latency_ms=result.model_load_latency_ms,
                inference_latency_ms=result.inference_latency_ms, warnings=tuple(result.warnings) + ("Isolated BGE reranker failed; metadata fallback was used.",),
                scored_items=result.scored_items, scoring_method=result.scoring_method, fallback_diagnostic=diagnostic,
            )
