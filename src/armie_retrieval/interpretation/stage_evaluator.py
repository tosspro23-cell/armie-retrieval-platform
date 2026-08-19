"""Small, deterministic stage-level evaluator for Gate 3F development fixtures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .staged import SemanticRole, StagedResult


@dataclass(frozen=True)
class StageGold:
    request_id: str
    roles: dict[str, SemanticRole]
    expected_fields: dict[str, str] | None = None


def role_metrics(gold: Iterable[StageGold], predictions: dict[str, StagedResult]) -> dict[str, float | int]:
    pairs = []
    for item in gold:
        result = predictions[item.request_id]
        predicted = {span.text.lower(): role.role for span, role in zip(result.spans, result.roles)}
        for text, expected in item.roles.items():
            pairs.append((expected, predicted.get(text.lower())))
    total = len(pairs)
    exact = sum(actual == expected for expected, actual in pairs)
    false_required = sum(actual is SemanticRole.REQUIRED and expected is not SemanticRole.REQUIRED for expected, actual in pairs)
    false_excluded = sum(actual is SemanticRole.EXCLUDED and expected is not SemanticRole.EXCLUDED for expected, actual in pairs)
    context_total = sum(expected is SemanticRole.CONTEXT_ONLY for expected, _ in pairs)
    context_correct = sum(expected is SemanticRole.CONTEXT_ONLY and actual is SemanticRole.CONTEXT_ONLY for expected, actual in pairs)
    preferred_total = sum(expected is SemanticRole.PREFERRED for expected, _ in pairs)
    preferred_correct = sum(expected is SemanticRole.PREFERRED and actual is SemanticRole.PREFERRED for expected, actual in pairs)
    return {
        "role_accuracy": exact / total if total else 0.0,
        "false_required_rate": false_required / total if total else 0.0,
        "false_excluded_rate": false_excluded / total if total else 0.0,
        "context_only_accuracy": context_correct / context_total if context_total else 0.0,
        "preferred_accuracy": preferred_correct / preferred_total if preferred_total else 0.0,
        "role_cases": total,
    }
