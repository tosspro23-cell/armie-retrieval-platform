"""JSON-line worker for isolated Torch/CrossEncoder reranking.

This module intentionally imports neither ARMIE runtime modules nor FAISS.  It is
started as ``python -m armie_retrieval.rerankers.worker`` so macOS can keep the
FAISS OpenMP runtime in the parent process and Torch's OpenMP runtime here.
"""

from __future__ import annotations

import json
import math
import sys
import time
from typing import Any


def _device(requested: str) -> str:
    if requested != "auto":
        return requested
    try:
        import torch
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def _error(request_id: str | None, error_type: str, message: str, guidance: str = "") -> dict[str, Any]:
    return {"request_id": request_id, "status": "error", "error_type": error_type, "message": message, "guidance": guidance}


def handle(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        return _error(request_id, "invalid_request", "request_id must be a non-empty string.")
    candidates = request.get("candidates")
    if not isinstance(candidates, list):
        return _error(request_id, "invalid_request", "candidates must be a list.")
    ids = [item.get("id") for item in candidates if isinstance(item, dict)]
    if len(ids) != len(candidates) or any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        return _error(request_id, "invalid_request", "candidates must contain unique non-empty string IDs.")
    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        return _error(request_id, "dependency_unavailable", "sentence-transformers is required.", "Install the model extras before running BGE reranking.")
    device = _device(str(request.get("device", "auto")))
    model_name = str(request.get("model", "BAAI/bge-reranker-v2-m3"))
    started = time.perf_counter()
    try:
        try:
            model = CrossEncoder(model_name, device=device, local_files_only=True)
        except TypeError:
            model = CrossEncoder(model_name, device=device)
    except Exception as exc:
        return _error(request_id, "model_unavailable", f"Model {model_name!r} is not available locally.", f"Download it explicitly with `huggingface-cli download {model_name}`. Internal error: {exc}")
    load_ms = (time.perf_counter() - started) * 1000
    inference_started = time.perf_counter()
    pairs = [(str(request.get("query", "")), str(item.get("document", ""))) for item in candidates]
    try:
        try:
            values = model.predict(pairs, batch_size=int(request.get("batch_size", 8)), show_progress_bar=False)
        except TypeError:
            values = model.predict(pairs, batch_size=int(request.get("batch_size", 8)))
    except Exception as exc:
        return _error(request_id, "inference_failure", f"Cross-encoder inference failed: {exc}")
    inference_ms = (time.perf_counter() - inference_started) * 1000
    scores = []
    for candidate_id, value in zip(ids, values):
        try:
            score = float(value)
        except (TypeError, ValueError):
            return _error(request_id, "invalid_score", f"Cross-encoder returned a non-numeric score for {candidate_id}.")
        if not math.isfinite(score):
            return _error(request_id, "invalid_score", f"Cross-encoder returned a non-finite score for {candidate_id}.")
        scores.append({"id": candidate_id, "raw_relevance_score": score})
    return {
        "request_id": request_id, "status": "ok", "actual_device": device,
        "model_load_latency_ms": load_ms, "inference_latency_ms": inference_ms,
        "scores": scores, "warnings": [],
        "worker_modules": {"torch_loaded": "torch" in sys.modules, "faiss_loaded": "faiss" in sys.modules},
    }


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        print(json.dumps(_error(None, "invalid_json", "Worker request is not valid JSON.", str(exc))))
        return 0
    if not isinstance(payload, dict):
        print(json.dumps(_error(None, "invalid_request", "Worker request must be a JSON object.")))
        return 0
    print(json.dumps(handle(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
