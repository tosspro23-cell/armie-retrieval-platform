"""Gate 3I: deterministic span proposals with model-only role classification."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from armie_retrieval.interpretation.staged import detect_spans
from armie_retrieval.planners.ollama import OllamaStructuredLLMClient

ROLES = {"REQUIRED", "EXCLUDED", "PREFERRED", "CONTEXT_ONLY", "UNSUPPORTED", "AMBIGUOUS"}


def expected_for(item, span_text):
    for phrase, role in item["roles"].items():
        if phrase.lower() == span_text.lower():
            return role
    for phrase, role in item["roles"].items():
        if span_text.lower() in phrase.lower() or phrase.lower() in span_text.lower():
            return role
    return None


def classify(client, request, span):
    prompt = (
        "Classify ONLY the supplied candidate phrase. Return exactly one JSON object "
        "with one key role and one value from REQUIRED, EXCLUDED, PREFERRED, "
        "CONTEXT_ONLY, UNSUPPORTED, AMBIGUOUS. Do not rewrite the phrase, emit "
        "spans, offsets, explanations, fields, operators, or values. Use the full "
        "request only to resolve scope and negation.\n"
        f"Request: {request}\nCandidate phrase: {span}\n"
    )
    payload = client.complete(prompt=prompt)
    role = payload.get("role") if isinstance(payload, dict) else None
    return role if role in ROLES and set(payload) <= {"role"} else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text())
    state = {
        "identity": f"gate3i-{args.model}-role-only-v1",
        "fixture": fixture["artifact_id"],
        "model": args.model,
        "items": {},
    }
    if args.checkpoint.exists():
        old = json.loads(args.checkpoint.read_text())
        if old.get("identity") != state["identity"] or old.get("fixture") != state["fixture"]:
            raise SystemExit("checkpoint identity mismatch")
        state = old

    client = OllamaStructuredLLMClient(args.model, timeout_seconds=args.timeout)
    stage1 = []
    for item in fixture["items"]:
        proposals = detect_spans(item["request"])
        stage1.append({
            "id": item["id"],
            "proposed": len(proposals),
            "gold": len(item["roles"]),
            "matched": sum(expected_for(item, span.text) is not None for span in proposals),
            "overlap": len({(span.start, span.end) for span in proposals}) != len(proposals),
            "boundary_valid": sum(span.text in item["request"] for span in proposals) / max(1, len(proposals)),
        })
        for span in proposals:
            key = f"{item['id']}::{span.span_id}"
            if key in state["items"]:
                continue
            started = time.perf_counter()
            try:
                role = classify(client, item["request"], span.text)
                record = {"id": item["id"], "span_id": span.span_id, "span": span.text, "expected": expected_for(item, span.text), "role": role, "schema_valid": role is not None, "latency_ms": (time.perf_counter() - started) * 1000, "model_calls": 1, "status": "completed"}
            except Exception as exc:
                record = {"id": item["id"], "span_id": span.span_id, "span": span.text, "expected": expected_for(item, span.text), "role": None, "schema_valid": False, "latency_ms": (time.perf_counter() - started) * 1000, "model_calls": 0, "status": "error", "error": str(exc)}
            state["items"][key] = record
            args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
            args.checkpoint.write_text(json.dumps(state, indent=2, sort_keys=True))

    rows = list(state["items"].values())
    valid = [row for row in rows if row["schema_valid"]]
    per_role = defaultdict(list)
    for row in valid:
        per_role[row["expected"]].append(row["role"] == row["expected"])
    latencies = [row["latency_ms"] for row in rows]
    metrics = {
        "completion_coverage": len(rows) / max(1, sum(row["proposed"] for row in stage1)),
        "schema_validity": len(valid) / max(1, len(rows)),
        "role_accuracy": sum(row["role"] == row["expected"] for row in valid) / max(1, len(valid)),
        "false_required": sum(row["role"] == "REQUIRED" and row["expected"] != "REQUIRED" for row in valid) / max(1, len(valid)),
        "false_excluded": sum(row["role"] == "EXCLUDED" and row["expected"] != "EXCLUDED" for row in valid) / max(1, len(valid)),
        "mean_latency_ms": statistics.mean(latencies) if latencies else 0,
        "p50_latency_ms": statistics.median(latencies) if latencies else 0,
        "p95_latency_ms": sorted(latencies)[max(0, int(.95 * len(latencies)) - 1)] if latencies else 0,
        "model_calls": sum(row["model_calls"] for row in rows),
    }
    result = {
        "identity": state["identity"],
        "fixture": state["fixture"],
        "fixture_sha256": hashlib.sha256(args.fixture.read_bytes()).hexdigest(),
        "stage1": stage1,
        "metrics": metrics,
        "per_role": {key: {"accuracy": sum(values) / len(values), "total": len(values)} for key, values in per_role.items()},
        "false_cases": [row for row in valid if row["role"] in {"REQUIRED", "EXCLUDED"} and row["role"] != row["expected"]],
        "rows": rows,
    }
    Path(".artifacts/v051_gate3i_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"identity": result["identity"], "metrics": metrics, "per_role": result["per_role"]}, indent=2))


if __name__ == "__main__":
    main()
