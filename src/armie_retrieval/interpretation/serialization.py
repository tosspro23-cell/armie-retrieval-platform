"""Canonical serialization helpers for Gate 1 benchmark artifacts."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any


def canonical_jsonl(records: Iterable[Mapping[str, Any]]) -> bytes:
    """Serialize records deterministically for reviewable fingerprints."""
    lines = [json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for record in records]
    return ("\n".join(lines) + "\n").encode("utf-8")


def fingerprint_records(records: Iterable[Mapping[str, Any]]) -> str:
    return hashlib.sha256(canonical_jsonl(records)).hexdigest()
