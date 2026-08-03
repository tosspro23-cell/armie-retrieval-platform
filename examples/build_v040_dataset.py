"""Build and validate the v0.4.0 Expert Discovery dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.datasets import build_dataset, load_dataset
from armie_retrieval.relevance import draft_judgements, generate_benchmark_queries, judgement_checksum


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default=".artifacts/datasets/expert_discovery_v1")
    args = parser.parse_args()
    manifest = build_dataset(args.output, size=args.size, seed=args.seed)
    profiles = load_dataset(args.output)
    queries = generate_benchmark_queries(seed=args.seed)
    judgements = draft_judgements(queries, profiles[: min(len(profiles), 250)])
    print(f"dataset={manifest.dataset_id}:{manifest.dataset_version} records={manifest.record_count} checksum={manifest.checksum}")
    print(f"queries={len(queries)} draft_judgements={len(judgements)} judgement_checksum={judgement_checksum(judgements)}")
    print("Review draft judgements before treating them as benchmark ground truth.")


if __name__ == "__main__":
    main()
