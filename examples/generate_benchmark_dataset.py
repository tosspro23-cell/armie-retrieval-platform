"""Generate a scalable, index-independent Expert Discovery benchmark corpus."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from armie_retrieval.benchmarking import generate_benchmark_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=50, help="Corpus size; 50, 200, and 500 are recommended benchmark scales")
    parser.add_argument("--output", default=".artifacts/benchmark")
    args = parser.parse_args()
    dataset = generate_benchmark_dataset(args.output, size=args.size)
    print(f"Generated {len(dataset.experts)} experts at {dataset.root / 'knowledge'}")


if __name__ == "__main__":
    main()
