"""Versioned Expert Discovery dataset contracts and deterministic builders."""

from .generator import build_dataset, load_dataset, validate_dataset
from .models import (
    DatasetManifest,
    EmploymentRecord,
    ExpertProfile,
    ProjectRecord,
    SourceReference,
)

__all__ = [
    "DatasetManifest",
    "EmploymentRecord",
    "ExpertProfile",
    "ProjectRecord",
    "SourceReference",
    "build_dataset",
    "load_dataset",
    "validate_dataset",
]
