"""Resumable bounded Gate 3F-R qwen span/role development comparison."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from armie_retrieval.interpretation import ModelAssistedStagedExtractor


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--model", default="qwen3:4b")
    args = ap.parse_args()
    fixture = json.loads(args.fixture.read_text())
    state = {"identity": f"staged-{args.model}-span-role-v1", "model": args.model, "fixture": fixture["artifact_id"], "items": {}}
    if args.checkpoint.exists():
        old = json.loads(args.checkpoint.read_text())
        if old.get("identity") != state["identity"] or old.get("fixture") != state["fixture"]:
            raise SystemExit("checkpoint identity mismatch")
        state = old
    arm = ModelAssistedStagedExtractor(model=args.model, timeout_seconds=args.timeout)
    for item in fixture["items"]:
        if item["id"] in state["items"]:
            continue
        result = arm.extract(item["request"], request_id=item["id"])
        state["items"][item["id"]] = {"model_calls": result.model_calls, "latency_ms": result.latency_ms, "metrics": result.metrics, "status": "completed", "roles": [{"text": span.text, "role": result.roles[i].role.value} for i, span in enumerate(result.spans)], "constraints": [asdict(c) for c in result.interpretation.constraints + result.interpretation.exclusions]}
        args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
        args.checkpoint.write_text(json.dumps(state, indent=2, sort_keys=True))
    print(json.dumps({"identity": state["identity"], "fixture": state["fixture"], "completed": len(state["items"]), "model_calls": sum(v["model_calls"] for v in state["items"].values()), "mean_latency_ms": sum(v["latency_ms"] for v in state["items"].values()) / len(state["items"])}, indent=2))


if __name__ == "__main__":
    main()
