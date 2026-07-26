"""Production StructuredLLMClient backed by a locally running Ollama service."""

from __future__ import annotations

import json
from typing import Any, Mapping

import requests


class OllamaPrerequisiteError(RuntimeError):
    """Raised when a local Ollama service or configured model is unavailable."""


class OllamaStructuredLLMClient:
    """Generate validated JSON planning decisions from a configurable local model.

    This is a planner client only: it never accesses knowledge providers, indexes,
    or retrieval infrastructure.
    """

    def __init__(self, model: str, *, base_url: str = "http://127.0.0.1:11434", timeout_seconds: float = 90.0, session=requests) -> None:
        if not model:
            raise ValueError("An Ollama model name must be configured")
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = session

    @property
    def model(self) -> str:
        return self._model

    def validate_model_available(self) -> None:
        try:
            response = self._session.get(f"{self._base_url}/api/tags", timeout=self._timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaPrerequisiteError(
                f"Ollama is unavailable at {self._base_url}. Start it with `ollama serve` and retry."
            ) from exc
        models = {entry.get("name") for entry in response.json().get("models", [])}
        if self._model not in models:
            raise OllamaPrerequisiteError(
                f"Configured Ollama model {self._model!r} is not installed. Run `ollama pull {self._model}` and retry."
            )

    def complete(self, *, prompt: str) -> Mapping[str, Any]:
        self.validate_model_available()
        try:
            response = self._session.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt + " Return only a JSON object.",
                    "format": "json",
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0},
                },
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            parsed = json.loads(payload["response"])
        except (requests.RequestException, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Ollama did not return a valid structured planning response") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError("Ollama structured planning response must be a JSON object")
        return parsed
