"""Versioned Expert Discovery dataset contracts and deterministic builders."""

from .generator import build_dataset, load_dataset, validate_dataset
from .v2 import (
    V2DocumentProfileGenerator,
    V2ExpertProfile,
    V2Judgement,
    V2JudgementBuilder,
    V2Manifest,
    V2Query,
    V2QueryGenerator,
    audit_v2_pilot,
    build_v2_pilot,
    pipeline_boundaries,
    write_audit,
)
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
    "V2DocumentProfileGenerator",
    "V2ExpertProfile",
    "V2Judgement",
    "V2JudgementBuilder",
    "V2Manifest",
    "V2Query",
    "V2QueryGenerator",
    "audit_v2_pilot",
    "build_v2_pilot",
    "pipeline_boundaries",
    "write_audit",
]
