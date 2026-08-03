"""Deterministic, licence-safe Expert Discovery corpus generation and validation."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from random import Random
from typing import Iterable

from .models import DatasetManifest, EmploymentRecord, ExpertProfile, ProjectRecord, SourceReference


GENERATOR_VERSION = "expert-discovery-generator-0.4.0"
PROJECTION_VERSION = "expert-search-projection-v1"
INDUSTRIES = ("healthcare", "financial services", "energy", "retail", "manufacturing", "technology")
TECHNOLOGIES = ("Azure AI", "RAG", "Elasticsearch", "FAISS", "semantic search", "MLOps", "Python", "knowledge graph")
ROLES = ("Search Engineer", "AI Platform Lead", "Data Scientist", "Principal Consultant", "ML Engineer")
LOCATIONS = ("Portugal", "United Kingdom", "Spain", "Poland", "Germany")
ORGANIZATIONS = ("Northstar Health", "Atlas Financial", "Meridian Energy", "Nova Systems", "Orion Retail")


def _projection(profile: ExpertProfile) -> dict:
    """Build a stable, field-bounded search projection."""
    return {
        "expert_id": profile.expert_id,
        "display_name": profile.display_name,
        "headline": profile.headline,
        "summary": profile.summary,
        "skills": list(profile.skills),
        "industries": list(profile.industries),
        "technologies": list(profile.technologies),
        "roles": list(profile.roles),
        "locations": list(profile.locations),
        "project_titles": [project.title for project in profile.projects],
        "project_descriptions": [project.description for project in profile.projects],
        "project_industries": [project.industry for project in profile.projects],
        "employer_names": [employer.organization for employer in profile.employers],
        "employer_descriptions": [employer.description for employer in profile.employers],
        "delivery_evidence": [project.delivery_evidence for project in profile.projects],
    }


def _profile(index: int, rng: Random) -> ExpertProfile:
    industry = INDUSTRIES[index % len(INDUSTRIES)]
    technology = TECHNOLOGIES[index % len(TECHNOLOGIES)]
    secondary = TECHNOLOGIES[(index + 3) % len(TECHNOLOGIES)]
    role = ROLES[index % len(ROLES)]
    location = LOCATIONS[index % len(LOCATIONS)]
    organization = ORGANIZATIONS[index % len(ORGANIZATIONS)]
    years = 5 + rng.randrange(21)
    expert_id = f"expert-{index + 1:05d}"
    project = ProjectRecord(
        project_id=f"project-{index + 1:05d}",
        title=f"{industry.title()} {technology} Discovery Platform",
        client_type="enterprise",
        industry=industry,
        role=role,
        technologies=[technology, secondary],
        skills=[technology, secondary, "retrieval evaluation"],
        description=(f"Delivered a production {technology} and retrieval system for {industry} teams, "
                     f"including measurable search quality and operational evidence."),
        start_date=date(2018 + index % 6, 1, 1),
        end_date=date(2020 + index % 6, 12, 31),
        delivery_evidence="project_delivery_record",
    )
    profile = ExpertProfile(
        expert_id=expert_id,
        display_name=f"Expert {index + 1:05d}",
        headline=f"{role} focused on {technology} and retrieval quality",
        summary=(f"{years} years building measurable AI search systems for {industry}; "
                 f"hands-on delivery with {technology} and {secondary}."),
        skills=[technology, secondary, "ranking", "evaluation"],
        industries=[industry],
        technologies=[technology, secondary],
        roles=[role],
        seniority="senior" if years >= 8 else "mid",
        employers=[EmploymentRecord(
            organization=organization,
            role=role,
            years=[2018 + index % 5, 2019 + index % 5],
            industry=industry,
            description=f"Worked on {industry} data products and {technology} delivery.",
        )],
        projects=[project],
        locations=[location],
        languages=["English", "Portuguese" if location == "Portugal" else "German"],
        years_experience=years,
        certifications=["Cloud Architecture"] if index % 4 == 0 else [],
        availability_status="available" if index % 5 else "engaged",
        source_type="synthetic_reference",
        source_provenance=[SourceReference(
            source_id=f"generator-{GENERATOR_VERSION}",
            source_type="deterministic_generator",
            provenance_kind="generated",
            note="Licence-safe synthetic reference profile; not a real person.",
        )],
        synthetic_fields=["all_fields"],
    )
    profile.search_document = _projection(profile)
    return profile


def _canonical(records: Iterable[ExpertProfile]) -> bytes:
    payload = [record.model_dump(mode="json") for record in records]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_dataset(output_root: str | Path, *, size: int = 10_000, seed: int = 42, dataset_version: str = "v1") -> DatasetManifest:
    if not 1 <= size <= 100_000:
        raise ValueError("size must be between 1 and 100000")
    root = Path(output_root)
    knowledge = root / "knowledge"
    knowledge.mkdir(parents=True, exist_ok=True)
    records = tuple(_profile(index, Random(seed + index)) for index in range(size))
    content = _canonical(records)
    checksum = hashlib.sha256(content).hexdigest()
    (knowledge / "experts.json").write_bytes(content)
    manifest = DatasetManifest(
        dataset_id="expert-discovery",
        dataset_version=dataset_version,
        schema_version="expert-profile-v1",
        record_count=len(records),
        seed=seed,
        generator_version=GENERATOR_VERSION,
        projection_version=PROJECTION_VERSION,
        licences=["CC0-like synthetic reference data"],
        generated_at="deterministic",
        checksum=checksum,
    )
    (root / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    validate_dataset(root)
    return manifest


def load_dataset(root: str | Path) -> tuple[ExpertProfile, ...]:
    path = Path(root) / "knowledge" / "experts.json"
    if not path.exists():
        raise FileNotFoundError(f"dataset source not found: {path}")
    return tuple(ExpertProfile.model_validate(record) for record in json.loads(path.read_text(encoding="utf-8")))


def validate_dataset(root: str | Path) -> DatasetManifest:
    root = Path(root)
    manifest = DatasetManifest.model_validate_json((root / "manifest.json").read_text(encoding="utf-8"))
    records = load_dataset(root)
    ids = [record.expert_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate expert IDs")
    if not records or any(not record.search_document for record in records):
        raise ValueError("dataset contains an empty search projection")
    checksum = hashlib.sha256(_canonical(records)).hexdigest()
    if checksum != manifest.checksum:
        raise ValueError("dataset checksum does not match manifest")
    if len(records) != manifest.record_count:
        raise ValueError("manifest record_count does not match dataset")
    return manifest
