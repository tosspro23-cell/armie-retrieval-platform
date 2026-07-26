"""Scalable, deterministic knowledge generation for offline validation.

The generated knowledge source is deliberately independent from index artifacts.
Run an IndexBuilder after generation to create searchable assets.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from random import Random

from armie_retrieval.models import ResultItem


_INDUSTRIES = ("healthcare", "financial services", "energy", "retail", "manufacturing")
_COUNTRIES = ("Portugal", "United Kingdom", "Spain", "Poland", "Germany")
_TECHNOLOGIES = ("Azure AI", "RAG", "knowledge graph", "FAISS", "semantic search", "MLOps")
_ORGANIZATIONS = ("ARMIE Labs", "Northstar Health", "Atlas Financial", "Meridian Energy", "Nova Systems")


@dataclass(frozen=True)
class BenchmarkDataset:
    root: Path
    experts: tuple[ResultItem, ...]
    queries: tuple[dict, ...]


def generate_benchmark_dataset(output_root: str | Path, *, size: int, seed: int = 42) -> BenchmarkDataset:
    """Write ``knowledge/`` sources for a 50, 200, 500, or arbitrary-size corpus."""
    if size <= 0:
        raise ValueError("Benchmark dataset size must be positive")
    root = Path(output_root)
    knowledge = root / "knowledge"
    knowledge.mkdir(parents=True, exist_ok=True)
    rng = Random(seed)
    experts: list[ResultItem] = []
    relationships: list[dict] = []
    organizations: dict[str, dict] = {}
    for index in range(size):
        industry = _INDUSTRIES[index % len(_INDUSTRIES)]
        country = _COUNTRIES[index % len(_COUNTRIES)]
        primary_technology = _TECHNOLOGIES[index % len(_TECHNOLOGIES)]
        secondary_technology = _TECHNOLOGIES[(index + 2) % len(_TECHNOLOGIES)]
        organization = _ORGANIZATIONS[index % len(_ORGANIZATIONS)]
        years = 5 + rng.randrange(16)
        expert_id = f"expert-{index + 1:03d}"
        item = ResultItem(
            id=expert_id,
            object_type="expert",
            title=f"Expert {index + 1}",
            content=(
                f"{years} years designing production {primary_technology} systems for "
                f"{industry}. Experience with {secondary_technology} and enterprise knowledge discovery."
            ),
            metadata={
                "industry": industry,
                "country": country,
                "skills": f"{primary_technology}, {secondary_technology}",
                "organization": organization,
                "technology": primary_technology,
                "projects": f"{industry.title()} Discovery {index + 1}",
            },
            sources=("benchmark",),
        )
        experts.append(item)
        organizations.setdefault(organization, {"id": organization.lower().replace(" ", "-"), "name": organization})
        relationships.extend(
            (
                {"source": expert_id, "relation": "WORKED_WITH", "target": organization},
                {"source": expert_id, "relation": "EXPERT_IN", "target": primary_technology},
                {"source": expert_id, "relation": "OPERATES_IN", "target": industry},
            )
        )

    queries = _benchmark_queries(experts)
    (knowledge / "experts.json").write_text(json.dumps([_to_record(item) for item in experts], indent=2), encoding="utf-8")
    (knowledge / "organizations.json").write_text(json.dumps(list(organizations.values()), indent=2), encoding="utf-8")
    (knowledge / "relationships.json").write_text(json.dumps(relationships, indent=2), encoding="utf-8")
    (knowledge / "queries.json").write_text(json.dumps(queries, indent=2), encoding="utf-8")
    return BenchmarkDataset(root=root, experts=tuple(experts), queries=tuple(queries))


def load_experts(dataset_root: str | Path) -> tuple[ResultItem, ...]:
    """Load generated knowledge without interacting with any index artifact."""
    source = Path(dataset_root) / "knowledge" / "experts.json"
    return tuple(ResultItem(**record) for record in json.loads(source.read_text(encoding="utf-8")))


def _benchmark_queries(experts: list[ResultItem]) -> list[dict]:
    cases: list[dict] = []
    for industry, technology in (("healthcare", "Azure AI"), ("financial services", "RAG"), ("energy", "knowledge graph")):
        relevant = [
            item.id for item in experts
            if item.metadata["industry"] == industry and item.metadata["technology"] == technology
        ]
        cases.append({
            "id": f"{industry.replace(' ', '-')}-{technology.replace(' ', '-').lower()}",
            "query": f"Find {industry} experts with {technology} experience",
            "relevant_ids": relevant,
        })
    return cases


def _to_record(item: ResultItem) -> dict:
    return {
        "id": item.id, "object_type": item.object_type, "title": item.title,
        "content": item.content, "metadata": dict(item.metadata), "score": item.score,
        "sources": list(item.sources), "signals": dict(item.signals),
    }
