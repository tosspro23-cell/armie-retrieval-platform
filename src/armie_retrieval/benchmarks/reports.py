"""Machine-readable and Markdown benchmark report rendering."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def render_report(run: dict[str, Any], output_root: str | Path) -> tuple[Path, Path]:
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{run['manifest']['run_id']}.json"
    markdown_path = root / f"{run['manifest']['run_id']}.md"
    json_path.write_text(json.dumps(run, indent=2, sort_keys=True), encoding="utf-8")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in run["rows"]:
        grouped[row["category"]].append(row)
    lines = [f"# Benchmark {run['manifest']['run_id']}", "", f"Profile: **{run['manifest']['profile']['name']}**", "", "| Category | NDCG@K | Recall@K | Precision@K | MRR |", "|---|---:|---:|---:|---:|"]
    for category, rows in sorted(grouped.items()):
        average = lambda name: sum(float(row["metrics"].get(name, 0.0)) for row in rows) / len(rows)
        lines.append(f"| {category} | {average('ndcg_at_k'):.3f} | {average('recall_at_k'):.3f} | {average('precision_at_k'):.3f} | {average('mrr'):.3f} |")
    lines.extend(["", f"Total runner latency: **{run['latency_ms']:.2f} ms**", "", "Provider-specific scores are not directly comparable; use the manifest and failure rows for interpretation."])
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path
