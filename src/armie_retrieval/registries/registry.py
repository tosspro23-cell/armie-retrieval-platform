"""Small capability-aware registry used for plugin resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Iterable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Registration(Generic[T]):
    name: str
    component: T
    capabilities: frozenset[str]
    version: str
    priority: int
    health_status: str
    metadata: dict[str, Any]


class ComponentRegistry(Generic[T]):
    """Plugin registry with capability, health, version, and priority resolution."""

    def __init__(self) -> None:
        self._entries: dict[str, Registration[T]] = {}

    def register(
        self,
        name: str,
        component: T,
        *,
        capabilities: set[str] | frozenset[str],
        version: str = "0.1.0",
        priority: int = 100,
        health_status: str = "healthy",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if name in self._entries:
            raise ValueError(f"Duplicate component registration: {name}")
        self._entries[name] = Registration(
            name, component, frozenset(capabilities), version, priority,
            health_status, dict(metadata or {}),
        )

    def resolve(self, name: str) -> T:
        try:
            return self._entries[name].component
        except KeyError as exc:
            raise KeyError(f"Unknown component: {name}") from exc

    def capabilities(self) -> frozenset[str]:
        return frozenset().union(*(entry.capabilities for entry in self._entries.values()))

    def discover(self, *, capability: str | None = None, healthy_only: bool = True) -> tuple[Registration[T], ...]:
        entries: Iterable[Registration[T]] = self._entries.values()
        if capability:
            entries = (entry for entry in entries if capability in entry.capabilities)
        if healthy_only:
            entries = (entry for entry in entries if entry.health_status == "healthy")
        return tuple(sorted(entries, key=lambda entry: entry.priority, reverse=True))

    def resolve_capability(self, capability: str) -> T:
        matches = self.discover(capability=capability)
        if not matches:
            raise KeyError(f"No healthy component provides capability: {capability}")
        return matches[0].component

    def set_health(self, name: str, health_status: str) -> None:
        entry = self._entries[name]
        self._entries[name] = Registration(
            entry.name, entry.component, entry.capabilities, entry.version,
            entry.priority, health_status, entry.metadata,
        )


class RetrieverRegistry(ComponentRegistry[T]):
    pass


class ProcessorRegistry(ComponentRegistry[T]):
    pass


class ProviderRegistry(ComponentRegistry[T]):
    pass
