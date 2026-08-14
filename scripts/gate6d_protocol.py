"""Frozen Gate 6D constraint-aware evaluation protocol."""
from __future__ import annotations

import hashlib
import json
from typing import Any

PROTOCOL_ID = "v0.5-constraint-aware-eval-protocol-v1"
BENCHMARK_FINGERPRINT = "6622e4604edc34ad481be7a65086df4b8d1318c185126f3bab1f6023360822eb"

PROTOCOL = {
    "protocol_id": PROTOCOL_ID,
    "objective": "maximize semantic relevance subject to all supported hard constraints being satisfied",
    "primary_metrics": {
        "eligible_ndcg_at_5": "gain over relevant-and-eligible judgement universe; ineligible candidates contribute zero gain",
        "eligible_precision_at_5": "returned relevant-and-eligible / returned Top-5 count",
        "eligible_mrr": "reciprocal rank of first returned relevant-and-eligible candidate",
        "eligible_recall_at_10": "retrieved relevant-and-eligible in Top-10 / all relevant-and-eligible in full judgement universe",
        "eligible_fill_at_5": "returned relevant-and-eligible / min(5, eligible supply); zero supply is not_applicable",
        "required_constraint_satisfaction_at_5": "returned eligible / returned Top-5 count",
        "constraint_violation_at_5": "returned ineligible / returned Top-5 count",
        "prohibited_constraint_violation_at_5": "explicit exclusion violation / applicable returned Top-5 slots",
        "true_hard_negative_intrusion_at_5": "returned structured hard-negative / returned Top-5 count",
    },
    "diagnostic_metrics": ["raw_ndcg_at_5", "raw_precision_at_5", "raw_recall_at_10", "raw_mrr", "grade_3_hit_at_5"],
    "thresholds": {
        "eligible_ndcg_at_5_max_degradation": 0.05,
        "eligible_precision_at_5_max_degradation": 0.05,
        "eligible_mrr_max_degradation": 0.05,
        "eligible_recall_at_10_max_degradation": 0.05,
        "eligible_fill_at_5_max_degradation": 0.05,
        "supply_sufficient_non_inferior_query_fraction": 0.60,
        "constraint_violation_required_relative_reduction": 0.50,
        "prohibited_violation_required_maximum": 0.01,
        "latency_warm_p95_max_multiplier_vs_c0": 1.50,
        "false_exclusion_maximum": 0,
    },
    "scarcity": "zero eligible supply is not_applicable for Eligible Fill and excluded from supply-sufficient query decisions",
    "c2_retention": "retain only with material eligible quality gain on meaningful supply-sufficient queries that justifies latency",
    "c3_reopening": "deferred unless C1/C2 complementary strengths or unsupported evidence-dependent constraints require it",
    "ann": {"k": 10, "size": 10, "num_candidates": 20},
}


def protocol_fingerprint(protocol: dict[str, Any] = PROTOCOL) -> str:
    return hashlib.sha256(json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


PROTOCOL_FINGERPRINT = protocol_fingerprint()
