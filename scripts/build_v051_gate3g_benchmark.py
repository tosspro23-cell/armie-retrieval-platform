"""Materialize the independent Gate 3G prospective promotion benchmark."""
from __future__ import annotations

import hashlib, json
from pathlib import Path

INDUSTRIES = ["Healthcare", "Financial Services", "Energy", "Retail", "Manufacturing", "Technology"]
LOCATIONS = ["London", "Lisbon", "Berlin", "Dublin", "Paris", "Madrid"]


def build() -> dict:
    items = []
    idx = 1
    for i in range(30):
        industry, years = INDUSTRIES[i % 6], 10 + (i % 5) * 5
        cases = [
            ("REQUIRED", f"must have at least {years} years of experience", "years_experience", "gte", years),
            ("EXCLUDED", f"exclude {industry}", "industry", "neq", industry.lower()),
            ("PREFERRED", f"preferably based in {LOCATIONS[i % 6]}", None, None, None),
            ("CONTEXT_ONLY", f"worked on {industry} AI products", None, None, None),
            ("UNSUPPORTED", f"worked with Partner{i + 1}", None, None, None),
            ("AMBIGUOUS", f"around {years} years", None, None, None),
        ]
        for role, phrase, field, operator, value in cases:
            item = {"id": f"g3g-{idx:03d}", "request": phrase, "stratum": role, "spans": [{"text": phrase, "role": role}]}
            if field:
                item["spans"][0].update({"field": field, "operator": operator, "value": value})
            items.append(item); idx += 1
    return {
        "benchmark_id": "v0.5.1-staged-interpretation-promotion-v1",
        "schema_version": "staged-promotion-benchmark-v1",
        "annotation_policy": "gate3g-role-policy-v1",
        "registry_id": "v0.5-c1-capability-registry-1",
        "candidate_identity": "deterministic-staged-v2-gate3fr",
        "purpose": "prospective_held_out_promotion_evidence",
        "items": items,
    }


def main() -> None:
    out = Path("tests/fixtures/v051_gate3g_promotion.json")
    payload = build()
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"benchmark_id": payload["benchmark_id"], "items": len(payload["items"]), "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
