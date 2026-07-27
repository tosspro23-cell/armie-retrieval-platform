"""Explicit runtime profile loading for deterministic and model-enhanced runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


class ProfileError(ValueError):
    """Raised when a requested runtime profile cannot be loaded."""


def profile_path(name: str, *, root: Path | None = None) -> Path:
    base = root or Path(__file__).resolve().parents[2] / "configs" / "profiles"
    path = base / f"{name}.yaml"
    if not path.exists():
        available = ", ".join(sorted(item.stem for item in base.glob("*.yaml"))) if base.exists() else "none"
        raise ProfileError(f"Unknown runtime profile {name!r}. Available profiles: {available}.")
    return path


def load_profile(name: str, *, root: Path | None = None) -> dict[str, Any]:
    """Load a profile. YAML is configuration only; no provider is auto-selected."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - package dependency protects normal installs
        raise ProfileError("PyYAML is required for runtime profiles. Install project dependencies.") from exc
    payload = yaml.safe_load(profile_path(name, root=root).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ProfileError(f"Profile {name!r} must contain a YAML mapping.")
    profile = dict(payload)
    profile.setdefault("name", name)
    return profile


def apply_overrides(profile: Mapping[str, Any], **overrides: Any) -> dict[str, Any]:
    """Apply explicit CLI overrides without mutating the loaded profile."""
    resolved = {key: (dict(value) if isinstance(value, Mapping) else value) for key, value in profile.items()}
    for section, values in overrides.items():
        if not values:
            continue
        target = dict(resolved.get(section, {}))
        target.update({key: value for key, value in values.items() if value is not None})
        resolved[section] = target
    return resolved
