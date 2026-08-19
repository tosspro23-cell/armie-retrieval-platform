#!/usr/bin/env python3
"""Materialize the frozen Gate 3 extraction evaluation fixture.

The fixture is deliberately separate from the Gate 2 development JSONL.  Each
Gate 1 stratum is represented six times with controlled, auditable language
variants; no result-dependent edits are possible because generation is
deterministic and the output is fingerprinted before arm execution.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from armie_retrieval.interpretation.serialization import fingerprint_records


VARIANTS = {
    "semantic-only": [
        "Find experts experienced with Azure AI architecture.",
        "Which experts have worked on Azure AI architecture?",
        "Locate people whose background includes Azure AI architecture.",
        "Who understands Azure AI architecture in practice?",
        "Show experts with a track record in Azure AI architecture.",
        "Find Azure AI architecture expertise without imposing a hard filter.",
    ],
    "numeric": [
        "Find experts with at least 20 years of experience.",
        "Find experts with 20 or more years of experience.",
        "Show experts with a minimum of twenty years' experience.",
        "Which experts have no less than 20 years in the field?",
        "Find people who have worked for 20+ years.",
        "Return experts whose experience is 20 years or greater.",
    ],
    "exclusion": [
        "Find Healthcare experts excluding Financial Services.",
        "Find Healthcare experts, but leave out Financial Services.",
        "Return Healthcare specialists who are not from Financial Services.",
        "Search for Healthcare experts and exclude Financial Services.",
        "Healthcare experts only, with Financial Services prohibited.",
        "Find Healthcare talent while avoiding Financial Services backgrounds.",
    ],
    "soft": [
        "Prefer senior candidates, ideally with Azure certification.",
        "Senior candidates would be ideal, but this is only a preference.",
        "It would be nice to have senior experts with Azure certification.",
        "Give preference to senior candidates where possible.",
        "A bonus would be seniority and Azure certification.",
        "Ideally choose someone senior, without making it mandatory.",
    ],
    "unsupported": [
        "Find Healthcare experts who delivered projects for Microsoft in the last 3 years.",
        "Which Healthcare experts worked with Microsoft recently?",
        "Find Healthcare specialists advised by Microsoft during the past three years.",
        "Show Healthcare experts who delivered for Microsoft in recent years.",
        "Find Healthcare people with Microsoft relationship evidence from the last three years.",
        "Who worked at Microsoft and has Healthcare expertise recently?",
    ],
    "ambiguous": [
        "Find senior Healthcare experts with substantial experience.",
        "Show experienced Healthcare leaders.",
        "Find Healthcare experts with significant senior-level background.",
        "Which Healthcare specialists have extensive experience?",
        "Locate seasoned people in Healthcare.",
        "Find highly experienced Healthcare professionals.",
    ],
    "contradiction": [
        "Find experts with at least 20 years and under 10 years.",
        "Find experts with 20 or more years but fewer than 10 years.",
        "Show people with a minimum of 20 years and less than 10 years.",
        "Find experts who have worked over 20 years and under 10 years.",
        "Return experts with >=20 years while requiring <10 years.",
        "Find people whose experience is at least 20 but below 10 years.",
    ],
    "hard": [
        "Find senior Healthcare experts with at least 20 years of experience.",
        "Return senior Healthcare experts with 20+ years of experience.",
        "Senior Healthcare specialists must have no less than 20 years' experience.",
        "Show senior experts in Healthcare with a minimum of twenty years.",
        "Find senior people working in Healthcare with 20 or more years.",
        "Only return senior Healthcare experts whose experience is at least 20 years.",
    ],
    "industry": [
        "Find experts in Healthcare.",
        "Which experts have Healthcare industry experience?",
        "Show people who worked in Healthcare.",
        "Return Healthcare specialists.",
        "Find experts whose industry is Healthcare.",
        "Healthcare is required for these experts.",
    ],
    "role": [
        "Find Search / Retrieval Engineer candidates where that role is required.",
        "Return engineers whose role is Search / Retrieval Engineer.",
        "Which Search / Retrieval Engineers should we consider?",
        "Find candidates working as Search / Retrieval Engineer.",
        "Search / Retrieval Engineer is mandatory for this request.",
        "Only show experts with the Search / Retrieval Engineer role.",
    ],
    "seniority": [
        "Find senior Healthcare experts.",
        "Return experts at senior level or above in Healthcare.",
        "Which Healthcare candidates are senior?",
        "Show Healthcare experts with seniority at least senior.",
        "Senior Healthcare expertise is required.",
        "Find principal-or-senior Healthcare experts.",
    ],
    "location": [
        "Find experts based in Portugal.",
        "Return candidates located in Portugal.",
        "Which experts are based in Portugal?",
        "Portugal-based experts are required.",
        "Show people whose location is Portugal.",
        "Only find experts working from Portugal.",
    ],
    "conjunction": [
        "Find senior Healthcare experts with at least 20 years.",
        "Return Healthcare experts who are senior and have 20+ years.",
        "Healthcare and seniority are both required, as is 20 years' experience.",
        "Show senior-level people in Healthcare with no less than 20 years.",
        "Find experts in Healthcare, senior or above, with 20 years minimum.",
        "Only return senior Healthcare experts with two decades of experience.",
    ],
    "maximum": [
        "Find experts under 20 years of experience.",
        "Return people with fewer than 20 years.",
        "Show experts with less than two decades of experience.",
        "Which candidates have at most 19 years?",
        "Find experts whose experience is below 20 years.",
        "Only return people under 20 years' experience.",
    ],
    "range": [
        "Find experts with between 10 and 20 years.",
        "Return people whose experience is from 10 through 20 years.",
        "Show candidates with 10–20 years of experience.",
        "Which experts have no fewer than 10 and no more than 20 years?",
        "Find experts in the ten to twenty year experience band.",
        "Only return people with experience between 10 and 20 years.",
    ],
    "unknown": [
        "Find experts in quantum gardening.",
        "Which people specialise in quantum gardening?",
        "Show candidates whose industry is quantum gardening.",
        "Return experts with quantum gardening experience.",
        "Find professionals from the quantum gardening sector.",
        "Quantum gardening expertise is required.",
    ],
    "temporal": [
        "Find experts active in Healthcare in the last three years.",
        "Return Healthcare experts with activity during the past three years.",
        "Which Healthcare specialists worked recently, within three years?",
        "Show experts in Healthcare whose experience is from the last three years.",
        "Find Healthcare candidates active over the previous three years.",
        "Only return Healthcare experts with recent three-year activity.",
    ],
    "relationship": [
        "Find experts who delivered projects for Microsoft.",
        "Which experts worked with Microsoft?",
        "Show candidates who advised Microsoft.",
        "Return experts with a Microsoft client relationship.",
        "Find people who worked at Microsoft.",
        "Only show experts who delivered work for Microsoft.",
    ],
    "paraphrase": [
        "People who have led teams building search relevance systems.",
        "Find leaders responsible for teams improving search relevance.",
        "Which experts managed search-ranking engineering teams?",
        "Show people who led relevance engineering delivery.",
        "Find technical leaders for search quality systems.",
        "Return experts with leadership of search relevance work.",
    ],
    "mixed": [
        "Senior Healthcare experts, ideally based in Portugal.",
        "Find senior people in Healthcare, with Portugal preferred.",
        "Healthcare is required; seniority is mandatory and Portugal is ideal.",
        "Return senior Healthcare candidates, preferably located in Portugal.",
        "Show Healthcare experts who must be senior, with Portugal as a preference.",
        "Find senior-level Healthcare experts where Portugal would be a bonus.",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="tests/fixtures/v051_gate1_gold.jsonl")
    parser.add_argument("--output", default="tests/fixtures/v051_gate3_eval.jsonl")
    args = parser.parse_args()
    source = [json.loads(line) for line in Path(args.source).read_text().splitlines() if line.strip()]
    by_prefix = {row["query_id"].rsplit("-", 1)[0]: row for row in source}
    by_prefix["hard"] = by_prefix["conjunction"]
    by_prefix["unknown"] = by_prefix["unknown-category"]
    records = []
    for prefix, variants in VARIANTS.items():
        if prefix not in by_prefix:
            raise SystemExit(f"missing Gate 1 stratum: {prefix}")
        base = by_prefix[prefix]
        for index, text in enumerate(variants, 1):
            row = dict(base)
            row["query_id"] = f"g3-{prefix}-{index:02d}"
            row["natural_language_request"] = text
            row["gate"] = "3"
            row["stratum"] = prefix
            if prefix == "industry":
                row["expected_constraints"] = [{"field": "industry", "operator": "eq", "value": "healthcare", "strength": "hard"}]
            elif prefix == "seniority":
                row["expected_constraints"] = [{"field": "seniority", "operator": "gte", "value": "principal" if "principal" in text.lower() else "senior", "strength": "hard"}]
            elif prefix == "ambiguous":
                row["expected_constraints"] = []
                row["state"] = "AMBIGUOUS"
            elif prefix == "role":
                row["expected_constraints"] = [{"field": "role", "operator": "eq", "value": "search / retrieval engineer", "strength": "hard"}]
            records.append(row)
    Path(args.output).write_text("\n".join(json.dumps(row, sort_keys=True) for row in records) + "\n")
    print(json.dumps({"benchmark_id": "v0.5.1-nl-constraint-extraction-eval-v1", "items": len(records), "fingerprint": fingerprint_records(records)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
