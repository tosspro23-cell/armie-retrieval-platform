"""Build and audit the Dataset v2 realism pilot without creating indexes."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from armie_retrieval.datasets.generator import build_dataset, load_dataset
from armie_retrieval.datasets.v2 import audit_v2_pilot, build_v2_pilot, write_audit
from armie_retrieval.relevance.contracts import QueryCategory, generate_benchmark_queries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("/tmp/armie-v040-dataset-v2-pilot-r2"))
    parser.add_argument("--size", type=int, default=750)
    parser.add_argument("--queries", type=int, default=40)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    build_v2_pilot(args.output, size=args.size, query_count=args.queries)
    with tempfile.TemporaryDirectory(prefix="armie-v1-comparison-") as temp:
        v1_root = Path(temp) / "v1"
        build_dataset(v1_root, size=min(args.size, 500), seed=42)
        targets = {category: 4 for category in QueryCategory}
        audit = audit_v2_pilot(args.output, v1_profiles=load_dataset(v1_root), v1_queries=generate_benchmark_queries(targets=targets))
    write_audit(args.output, audit)
    print(f"Dataset v2 pilot: {args.output}")
    print(f"Profiles: {audit['counts']['profiles']}; queries: {audit['counts']['queries']}")
    print(f"Summary duplicate rate: {audit['duplicates']['normalized_summary_duplicate_rate']:.2%}")
    print(f"Surface overlap lower than v1: {audit['v1_comparison']['v2_lower_overlap']}")


if __name__ == "__main__":
    main()
