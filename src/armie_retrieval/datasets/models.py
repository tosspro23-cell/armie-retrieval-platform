"""Typed, provenance-aware Expert Discovery domain contracts for v0.4.0."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


ProvenanceKind = Literal["sourced", "transformed", "manually_authored", "generated", "inferred"]


class SourceReference(BaseModel):
    source_id: str
    source_type: str
    provenance_kind: ProvenanceKind
    locator: str | None = None
    note: str | None = None


class EmploymentRecord(BaseModel):
    organization: str
    role: str
    years: list[int] = Field(default_factory=list)
    industry: str
    description: str
    provenance_kind: ProvenanceKind = "generated"

    @field_validator("years")
    @classmethod
    def valid_years(cls, value: list[int]) -> list[int]:
        if any(year < 1950 or year > 2100 for year in value):
            raise ValueError("employment years must be between 1950 and 2100")
        return value


class ProjectRecord(BaseModel):
    project_id: str
    title: str
    client_type: str
    industry: str
    role: str
    technologies: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    description: str
    start_date: date | None = None
    end_date: date | None = None
    delivery_evidence: str
    provenance_kind: ProvenanceKind = "generated"

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, value: date | None, info: Any) -> date | None:
        start = info.data.get("start_date")
        if value is not None and start is not None and value < start:
            raise ValueError("project end_date must not precede start_date")
        return value


class ExpertProfile(BaseModel):
    expert_id: str
    display_name: str
    headline: str
    summary: str
    skills: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    seniority: str | None = None
    employers: list[EmploymentRecord] = Field(default_factory=list)
    projects: list[ProjectRecord] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    years_experience: int | None = None
    certifications: list[str] = Field(default_factory=list)
    availability_status: str | None = None
    source_type: str
    source_provenance: list[SourceReference] = Field(default_factory=list)
    synthetic_fields: list[str] = Field(default_factory=list)
    schema_version: str = "expert-profile-v1"
    search_document: dict[str, Any] = Field(default_factory=dict)

    @field_validator("expert_id", "display_name", "headline", "summary", "source_type")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("required text fields cannot be empty")
        return value

    @field_validator("years_experience")
    @classmethod
    def valid_experience(cls, value: int | None) -> int | None:
        if value is not None and not 0 <= value <= 80:
            raise ValueError("years_experience must be between 0 and 80")
        return value


class DatasetManifest(BaseModel):
    dataset_id: str
    dataset_version: str
    schema_version: str
    record_count: int
    seed: int
    generator_version: str
    projection_version: str
    licences: list[str]
    generated_at: str
    checksum: str
