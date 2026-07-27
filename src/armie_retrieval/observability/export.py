"""Stable JSON trace export; generated files are runtime artifacts, not source files."""

from __future__ import annotations

from pathlib import Path
from time import strftime

from .models import RetrievalTrace


def export_trace(trace: RetrievalTrace, artifact_directory: str | Path = ".artifacts/traces") -> Path:
    directory = Path(artifact_directory)
    directory.mkdir(parents=True, exist_ok=True)
    safe_query_id = "".join(char if char.isalnum() or char in "-_" else "-" for char in trace.query_id)
    destination = directory / f"{safe_query_id}-{strftime('%Y%m%d-%H%M%S')}.json"
    destination.write_text(trace.to_json() + "\n", encoding="utf-8")
    return destination
