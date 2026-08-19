#!/usr/bin/env python3
"""Resumable, durable Gate 3C model evaluation harness."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Mapping

try:  # direct script execution with PYTHONPATH=scripts:src
    from run_v051_gate3_evaluation import Gate3Hybrid, Gate3Model, build_gold
    from armie_retrieval.interpretation import CascadeExtractorV2, OllamaStructuredExtractorV2, RuleExtractorV3
except ModuleNotFoundError:  # unittest/import package execution
    from scripts.run_v051_gate3_evaluation import Gate3Hybrid, Gate3Model, build_gold
    from armie_retrieval.interpretation import CascadeExtractorV2, OllamaStructuredExtractorV2, RuleExtractorV3
from armie_retrieval.interpretation import evaluate_interpretation, fingerprint_records

HARNESS_VERSION = "gate3c-resumable-v1"
CHECKPOINT_SCHEMA = "gate3c-item-checkpoint-v1"
AGGREGATION_VERSION = "gate3c-aggregation-v1"
PROMPT_FINGERPRINT = "gate3-structured-v1"
SCHEMA_ID = "nl-constraint-interpretation-v1"
REGISTRY_ID = "v0.5-c1-capability-registry-1"
DECODING = {"temperature": 0, "format": "json", "think": False, "stream": False}
TERMINAL = {"SUCCESS", "MODEL_CALL_FAILURE", "STRUCTURED_OUTPUT_FAILURE", "SCHEMA_VALIDATION_FAILURE", "ABSTENTION", "TIMEOUT"}

def frozen_identity(records: list[Mapping[str, Any]], arm: Any, *, timeout: float, retries: int) -> dict[str, Any]:
    model = getattr(getattr(arm, "inner", None), "model", None) or "qwen3:4b"
    if not isinstance(model, str):
        model = getattr(model, "model", "qwen3:4b")
    arm_identity = ("ollama-structured-qwen3-4b-v2-gate3d" if arm.identity.startswith("ollama-structured-qwen3-4b-v2")
                    else "ollama-structured-qwen3-4b-v1-gate3b-warm-persistent-v1" if arm.identity.startswith("ollama-")
                    else "hybrid-rule-plus-structured-qwen3-4b-v1-gate3b-warm-persistent-v1" if arm.identity.startswith("hybrid-")
                    else arm.identity)
    prompt_fp = getattr(getattr(arm, "inner", arm), "prompt_fingerprint", PROMPT_FINGERPRINT)
    return {"harness_version": HARNESS_VERSION, "checkpoint_schema": CHECKPOINT_SCHEMA,
            "benchmark_fingerprint": fingerprint_records(records), "item_count": len(records),
            "arm_identity": arm_identity, "implementation_identity": arm.identity, "model_identity": arm_identity, "model": model,
            "prompt_fingerprint": prompt_fp, "schema_identity": SCHEMA_ID,
            "registry_identity": REGISTRY_ID, "timeout_seconds": timeout, "max_retries": retries,
            "decoding": DECODING}

def _meta_path(checkpoint: Path) -> Path:
    return checkpoint.with_suffix(checkpoint.suffix + ".meta.json")

def _load_checkpoint(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def _write_meta(path: Path, identity: Mapping[str, Any]) -> None:
    meta = _meta_path(path)
    if meta.exists():
        if json.loads(meta.read_text()) != dict(identity):
            raise ValueError("checkpoint identity mismatch; refusing to resume or merge")
        return
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps(dict(identity), indent=2, sort_keys=True) + "\n")

def _append(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True, default=str) + "\n")
        handle.flush(); os.fsync(handle.fileno())

def _terminal_status(status: str) -> str:
    return "SUCCESS" if status == "COMPLETED" else "STRUCTURED_OUTPUT_FAILURE" if status == "INVALID_OUTPUT" else "MODEL_CALL_FAILURE"

def _result_row(record: Mapping[str, Any], result: Any, attempt: int) -> dict[str, Any]:
    row = {"checkpoint_schema": CHECKPOINT_SCHEMA, "query_id": record["query_id"], "stratum": record.get("stratum"),
           "status": _terminal_status(result.status), "source_status": result.status, "attempt": attempt,
           "latency_ms": result.latency_ms, "metadata": dict(result.metadata), "error": result.error}
    if result.interpretation is not None:
        row["predicted"] = result.interpretation.to_dict()
        row["metrics"] = evaluate_interpretation(build_gold(record), result.interpretation).__dict__
    return row

def run_resumable(records: list[Mapping[str, Any]], arm: Any, checkpoint: Path, *, timeout: float,
                  retries: int = 1, max_wall_clock: float | None = None,
                  interrupt_after: int | None = None, run_id: str | None = None) -> dict[str, Any]:
    identity = frozen_identity(records, arm, timeout=timeout, retries=retries); _write_meta(checkpoint, identity)
    existing = _load_checkpoint(checkpoint); expected = {str(r["query_id"]) for r in records}
    existing_ids = [str(row.get("query_id")) for row in existing]
    if len(existing_ids) != len(set(existing_ids)):
        raise ValueError("checkpoint contains duplicate query IDs")
    completed = {str(row["query_id"]): row for row in existing if row.get("status") in TERMINAL}
    if len(completed) != len(existing): raise ValueError("checkpoint contains non-terminal rows")
    if len(completed) > len(expected) or not set(completed).issubset(expected): raise ValueError("checkpoint contains IDs outside this frozen benchmark")
    started = time.monotonic(); processed = 0
    for record in records:
        query_id = str(record["query_id"])
        if query_id in completed: continue
        if max_wall_clock is not None and time.monotonic() - started >= max_wall_clock: break
        for attempt in range(1, retries + 2):
            try: result = arm.extract(record["natural_language_request"], request_id=query_id)
            except Exception as exc:
                result = type("Result", (), {"status": "NOT_RUN", "latency_ms": 0.0, "metadata": {}, "error": str(exc), "interpretation": None})()
            if result.status == "COMPLETED" or attempt > retries: break
        row = _result_row(record, result, attempt); _append(checkpoint, row); completed[query_id] = row; processed += 1
        if interrupt_after is not None and processed >= interrupt_after: raise KeyboardInterrupt("intentional Gate 3C development interruption after durable checkpoint")
    rows = list(completed.values()); ids = {str(row["query_id"]) for row in rows}
    integrity = {"expected": len(expected), "represented": len(ids), "duplicate_ids": len(rows) - len(ids),
                 "missing_ids": sorted(expected - ids), "all_terminal": all(row.get("status") in TERMINAL for row in rows)}
    successful = [row for row in rows if row["status"] == "SUCCESS"]
    report = {"run_id": run_id or identity["arm_identity"], "harness_identity": {"runner": HARNESS_VERSION, "checkpoint_schema": CHECKPOINT_SCHEMA, "aggregation": AGGREGATION_VERSION},
              "frozen_identity": identity, "execution": {"attempted": len(expected), "terminal": len(rows), "successful_structured_outputs": len(successful),
              "infrastructure_failures": sum(row["status"] == "MODEL_CALL_FAILURE" for row in rows), "structured_output_failures": sum(row["status"] == "STRUCTURED_OUTPUT_FAILURE" for row in rows),
              "wall_clock_seconds": time.monotonic() - started, "max_wall_clock_seconds": max_wall_clock, "retry_policy": {"max_retries": retries}},
              "integrity": integrity, "status": "COMPLETED" if not integrity["duplicate_ids"] and not integrity["missing_ids"] else "INCOMPLETE",
              "items": sorted(rows, key=lambda row: str(row["query_id"]))}
    return report

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--fixture", default="tests/fixtures/v051_gate3_eval.jsonl"); parser.add_argument("--manifest", default="docs/v0.5.1/gate3-evaluation-manifest.json"); parser.add_argument("--arm", choices=("model", "model2", "hybrid", "cascade", "rule3"), default="model"); parser.add_argument("--checkpoint", required=True); parser.add_argument("--output", required=True); parser.add_argument("--run-id", default="gate3-qwen3-4b-frozen-eval-v1"); parser.add_argument("--timeout", type=float, default=15.0); parser.add_argument("--retries", type=int, default=1); parser.add_argument("--max-wall-clock", type=float); parser.add_argument("--limit", type=int); parser.add_argument("--interrupt-after", type=int); args = parser.parse_args()
    records = [json.loads(line) for line in Path(args.fixture).read_text().splitlines() if line.strip()]
    manifest = json.loads(Path(args.manifest).read_text())
    if args.limit is None and (len(records) != manifest["item_count"] or fingerprint_records(records) != manifest["fingerprint"]):
        raise SystemExit("frozen Gate 3 fixture does not match manifest")
    records = records[:args.limit] if args.limit else records
    arm = {"model": Gate3Model(args.timeout), "model2": OllamaStructuredExtractorV2(timeout_seconds=args.timeout), "hybrid": Gate3Hybrid(args.timeout), "cascade": CascadeExtractorV2(timeout_seconds=args.timeout), "rule3": RuleExtractorV3()}[args.arm]
    try: report = run_resumable(records, arm, Path(args.checkpoint), timeout=args.timeout, retries=args.retries, max_wall_clock=args.max_wall_clock, interrupt_after=args.interrupt_after, run_id=args.run_id)
    except KeyboardInterrupt as exc: print(str(exc)); return
    Path(args.output).parent.mkdir(parents=True, exist_ok=True); Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"); print(json.dumps({"status": report["status"], "integrity": report["integrity"], "execution": report["execution"]}, indent=2))

if __name__ == "__main__": main()
