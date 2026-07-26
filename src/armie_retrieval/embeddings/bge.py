"""Configurable, local-only BGE embedding provider."""

from __future__ import annotations

from typing import Sequence


class EmbeddingPrerequisiteError(RuntimeError):
    """Raised when the configured local embedding model is unavailable."""


class BGEEmbeddingProvider:
    """SentenceTransformers provider with BGE-M3 as the configurable default.

    `local_files_only=True` is intentional: validation must never trigger an
    unapproved multi-gigabyte model download.
    """

    def __init__(self, model_name: str = "BAAI/bge-m3", *, device: str | None = None, local_files_only: bool = True) -> None:
        self._model_name = model_name
        self._device = device
        self._local_files_only = local_files_only
        self._model = None
        self._dimension: int | None = None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        self._ensure_model()
        assert self._dimension is not None
        return self._dimension

    def validate_model_available(self) -> None:
        self._ensure_model()

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self._ensure_model()
        vectors = self._model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self._model_name,
                device=self._device,
                local_files_only=self._local_files_only,
            )
            self._dimension = int(self._model.get_sentence_embedding_dimension())
        except ImportError as exc:
            raise EmbeddingPrerequisiteError(
                "sentence-transformers is required. Install project dependencies with `python3 -m pip install .`."
            ) from exc
        except Exception as exc:
            guidance = (
                f"Embedding model {self._model_name!r} is not available locally. "
                "Download it explicitly before validation, for example: "
                f"`huggingface-cli download {self._model_name}`."
            )
            raise EmbeddingPrerequisiteError(guidance) from exc
