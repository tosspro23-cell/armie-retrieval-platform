"""Run the deterministic local v0.4.0 benchmark foundation and emit reports."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.benchmarks import default_profiles, render_report, run_profile
from armie_retrieval.datasets import build_dataset, load_dataset
from armie_retrieval.relevance import draft_judgements, generate_benchmark_queries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=200)
    parser.add_argument("--output", default=".artifacts/v040-benchmark")
    args = parser.parse_args()
    dataset_root = Path(args.output) / "dataset"
    manifest = build_dataset(dataset_root, size=args.size)
    records = load_dataset(dataset_root)
    queries = generate_benchmark_queries()
    drafts = draft_judgements(queries, records)
    judgements = {}
    for judgement in drafts:
        judgements.setdefault(judgement.query_id, {})[judgement.expert_id] = judgement.grade
    for profile in default_profiles():
        run = run_profile(profile, queries, records, judgements, dataset_checksum=manifest.checksum)
        json_path, markdown_path = render_report(run, Path(args.output) / "reports")
        print(f"{profile.profile_id}: {json_path} {markdown_path}")


if __name__ == "__main__":
    main()
