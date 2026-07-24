"""Offline stores. Runtime is intentionally not given access to observations."""

from __future__ import annotations

from armie_retrieval.models import ExecutionObservation, Policy


class ObservationStore:
    def __init__(self) -> None:
        self._observations: list[ExecutionObservation] = []

    def append(self, observation: ExecutionObservation) -> None:
        self._observations.append(observation)

    def all(self) -> tuple[ExecutionObservation, ...]:
        return tuple(self._observations)


class PolicyRepository:
    def __init__(self) -> None:
        self._published: Policy | None = None

    def publish(self, policy: Policy) -> None:
        if self._published and policy.version <= self._published.version:
            raise ValueError("Published policy versions must increase")
        self._published = policy

    def latest(self) -> Policy | None:
        return self._published
