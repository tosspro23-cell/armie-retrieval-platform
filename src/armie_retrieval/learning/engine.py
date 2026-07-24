"""Rule-based offline policy optimisation for the first adaptive-learning loop."""

from __future__ import annotations

from collections import Counter

from armie_retrieval.learning.store import ObservationStore, PolicyRepository
from armie_retrieval.models import Policy


class LearningEngine:
    """Consumes observations offline and publishes a small, auditable policy update."""

    def optimize_and_publish(self, store: ObservationStore, repository: PolicyRepository) -> Policy:
        observations = store.all()
        unavailable_processors = {
            observation.details.get("processor")
            for observation in observations
            if observation.event_type == "unsupported_capability" and observation.details.get("processor")
        }
        slow_components = Counter(
            observation.component_name
            for observation in observations
            if observation.event_type == "latency_exceeded"
        )
        priority = {name: -count for name, count in slow_components.items()}
        current = repository.latest()
        version = (current.version if current else 0) + 1
        processors = tuple(processor for processor in ("deduplicate", "expert_rerank") if processor not in unavailable_processors)
        policy = Policy(
            version=version,
            processor_defaults=processors,
            retriever_priority=priority,
            rationale=tuple(
                [f"Excluded unsupported processor: {name}" for name in sorted(unavailable_processors)]
                + [f"Lowered priority after latency observations: {name}" for name in sorted(slow_components)]
            ),
        )
        repository.publish(policy)
        return policy
