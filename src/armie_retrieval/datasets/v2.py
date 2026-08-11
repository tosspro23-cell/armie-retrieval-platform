"""Controlled-synthetic Dataset v2 for realism and leakage validation.

The v2 corpus deliberately separates three deterministic pipelines:

* :class:`V2DocumentProfileGenerator` generates profile documents from
  canonical structured truth and document-only surface language.
* :class:`V2QueryGenerator` generates independent query language from the same
  ontology identifiers, but a different seed and query-only surface language.
* :class:`V2JudgementBuilder` grades canonical truth and evidence, never the
  generated text or retrieval results.

This module is a pilot-quality gate, not a replacement for Dataset v1.  The v1
generator and its checksum remain untouched and are intentionally imported only
for comparison in the audit helpers.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from random import Random
from statistics import mean, median
from typing import Any, Iterable, Literal

from pydantic import BaseModel, Field, field_validator

from armie_retrieval.relevance.contracts import QueryCategory


V2_DATASET_ID = "expert-discovery-v2-realism"
V2_DATASET_VERSION = "v2-realism-pilot-r2"
V2_SCHEMA_VERSION = "expert-profile-v2-realism"
V2_GENERATOR_VERSION = "expert-discovery-generator-v2-realism-0.2-r2"
V2_PROJECTION_VERSION = "expert-search-projection-v2-realism"
V2_ONTOLOGY_VERSION = "expert-discovery-ontology-0.2"
V2_SURFACE_LEXICON_VERSION = "surface-lexicon-v2-separated"
V2_RELATIONSHIP_VERSION = "relationship-model-v2"
V2_TEMPORAL_VERSION = "temporal-model-v2"
V2_EVIDENCE_VERSION = "evidence-model-v2"
V2_QUERY_VERSION = "expert-discovery-queries-v2-realism-0.2"
V2_JUDGEMENT_VERSION = "expert-discovery-judgements-v2-structured-0.2"


class V2Evidence(BaseModel):
    evidence_id: str
    evidence_kind: Literal[
        "skill_mention", "hands_on_delivery", "leadership", "advisory_exposure",
        "employer_relationship", "client_relationship", "certification", "explicit_span",
    ]
    source_id: str
    text_span: str
    subject_id: str
    object_id: str | None = None
    provenance_kind: Literal["synthetic_structured", "synthetic_narrative"] = "synthetic_structured"


class V2Relationship(BaseModel):
    edge_id: str
    subject_id: str
    predicate: Literal[
        "works_at", "delivered_for", "advised", "sold_to", "partnered_with", "vendor_of",
        "has_project", "uses_technology", "in_industry", "located_in", "speaks",
        "holds_certification",
    ]
    object_id: str
    object_type: Literal["expert", "employer", "client", "partner", "vendor", "project", "industry", "technology", "location", "language", "certification"]
    valid_from: date | None = None
    valid_to: date | None = None
    evidence_ids: list[str] = Field(default_factory=list)

    @field_validator("valid_to")
    @classmethod
    def valid_range(cls, value: date | None, info: Any) -> date | None:
        start = info.data.get("valid_from")
        if value is not None and start is not None and value < start:
            raise ValueError("relationship valid_to precedes valid_from")
        return value


class V2Employment(BaseModel):
    organization_id: str
    organization_name: str
    role: str
    industry: str
    start_date: date
    end_date: date | None = None
    current: bool = False
    evidence_ids: list[str] = Field(default_factory=list)


class V2Project(BaseModel):
    project_id: str
    title: str
    client_id: str
    client_name: str
    client_type: Literal["enterprise", "public_sector", "startup", "nonprofit"]
    industry: str
    role: str
    technologies: list[str]
    canonical_concepts: list[str]
    start_date: date
    end_date: date
    delivery_level: Literal["hands_on", "technical_lead", "advisory"]
    evidence_ids: list[str] = Field(default_factory=list)


class V2ExpertProfile(BaseModel):
    expert_id: str
    display_name: str
    headline: str
    summary: str
    canonical_concepts: list[str]
    skills: list[str]
    industries: list[str]
    technologies: list[str]
    roles: list[str]
    seniority: Literal["mid", "senior", "principal"]
    employers: list[V2Employment]
    projects: list[V2Project]
    locations: list[str]
    languages: list[str]
    certifications: list[str]
    advisory_areas: list[str]
    relationships: list[V2Relationship]
    evidence: list[V2Evidence]
    years_experience: int
    current_role: bool
    narrative_style: str
    opening_pattern: str = "unknown"
    verbosity_band: Literal["brief", "standard", "detailed"]
    source_provenance: str = "controlled_synthetic_reference"
    search_document: dict[str, Any] = Field(default_factory=dict)


class V2Query(BaseModel):
    query_id: str
    query_text: str
    category: QueryCategory
    canonical_required: list[str] = Field(default_factory=list)
    canonical_optional: list[str] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    canonical_prohibited: list[str] = Field(default_factory=list)
    industry_required: list[str] = Field(default_factory=list)
    organization_required: str | None = None
    relationship_required: list[str] = Field(default_factory=list)
    evidence_required: list[str] = Field(default_factory=list)
    role_required: list[str] = Field(default_factory=list)
    seniority_required: list[str] = Field(default_factory=list)
    semantic_bucket: Literal["exact", "partial", "semantic", "low_overlap"] = "exact"
    hard_negative_type: str | None = None
    temporal_start: date | None = None
    temporal_end: date | None = None
    expected_signals: list[str] = Field(default_factory=list)
    query_set_version: str = V2_QUERY_VERSION


class V2Judgement(BaseModel):
    query_id: str
    expert_id: str
    grade: Literal[0, 1, 2, 3]
    matched_concepts: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    violated_concepts: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    rationale_codes: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    review_status: Literal["draft_silver_rule_assisted", "draft_gold_structured_audit"]
    judgement_set_id: str = V2_JUDGEMENT_VERSION


class V2Manifest(BaseModel):
    dataset_id: str = V2_DATASET_ID
    dataset_version: str = V2_DATASET_VERSION
    schema_version: str = V2_SCHEMA_VERSION
    record_count: int
    query_count: int
    seed: int
    document_seed: int
    query_seed: int
    generator_version: str = V2_GENERATOR_VERSION
    projection_version: str = V2_PROJECTION_VERSION
    ontology_version: str = V2_ONTOLOGY_VERSION
    surface_lexicon_version: str = V2_SURFACE_LEXICON_VERSION
    relationship_model_version: str = V2_RELATIONSHIP_VERSION
    temporal_model_version: str = V2_TEMPORAL_VERSION
    evidence_model_version: str = V2_EVIDENCE_VERSION
    query_set_version: str = V2_QUERY_VERSION
    judgement_set_version: str = V2_JUDGEMENT_VERSION
    checksum: str
    generated_at: str = "deterministic"
    limitations: list[str] = Field(default_factory=lambda: [
        "controlled synthetic relevance benchmark",
        "9,496 duplicate normalized summaries in the 10,000-profile v1 corpus",
        "templated synthetic language and controlled-vocabulary leakage risk",
        "Gold is an independent structured audit, not external human ground truth",
    ])


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _normalized(text: str) -> str:
    return " ".join(_tokens(text))


def _sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


CANONICAL_CONCEPTS = (
    "semantic_search", "hybrid_retrieval", "retrieval_evaluation", "knowledge_graph",
    "generative_ai_delivery", "cloud_ai", "data_platform", "healthcare_ai",
    "financial_risk", "energy_transition", "retail_analytics", "mlops",
    "search_relevance", "production_python", "advisory_strategy", "technical_leadership",
)
DOCUMENT_SURFACES = {
    "semantic_search": ("meaning-aware search", "intent-sensitive discovery", "semantic retrieval"),
    "hybrid_retrieval": ("blended keyword and vector retrieval", "combined lexical and neural search", "hybrid search delivery"),
    "retrieval_evaluation": ("relevance measurement", "search-quality evaluation", "retrieval assessment"),
    "knowledge_graph": ("entity relationship modelling", "connected knowledge systems", "graph-based discovery"),
    "generative_ai_delivery": ("production generative AI", "LLM delivery", "grounded language systems"),
    "cloud_ai": ("cloud AI platforms", "managed machine-learning services", "cloud inference"),
    "data_platform": ("data platform engineering", "analytical data products", "data foundation work"),
    "healthcare_ai": ("care delivery technology", "health data programmes", "clinical technology"),
    "financial_risk": ("financial risk operations", "risk analytics", "regulated finance"),
    "energy_transition": ("energy transition", "power-sector analytics", "decarbonisation programmes"),
    "retail_analytics": ("retail decision systems", "commerce analytics", "customer operations"),
    "mlops": ("model operations", "ML lifecycle engineering", "reliable model delivery"),
    "search_relevance": ("ranking quality", "relevance engineering", "search effectiveness"),
    "production_python": ("Python services", "production Python", "maintainable Python systems"),
    "advisory_strategy": ("technology advisory", "delivery strategy", "technical due diligence"),
    "technical_leadership": ("technical leadership", "engineering direction", "architecture leadership"),
}
QUERY_SURFACES = {
    "semantic_search": ("sensemaking practitioners", "intent-centric indexing specialists"),
    "hybrid_retrieval": ("lexical-neural blend", "dual-signal matching"),
    "retrieval_evaluation": ("ranking diagnostics", "usefulness assessment"),
    "knowledge_graph": ("entity topology", "connected-fact reasoning"),
    "generative_ai_delivery": ("language-model deployment", "grounded generation"),
    "cloud_ai": ("managed inference operations", "hosted model services"),
    "data_platform": ("analytical foundations", "data-product stewardship"),
    "healthcare_ai": ("care-data programmes", "clinical informatics"),
    "financial_risk": ("regulated risk practice", "finance controls"),
    "energy_transition": ("power-sector transformation", "decarbonisation delivery"),
    "retail_analytics": ("commerce intelligence", "customer merchandising"),
    "mlops": ("model lifecycle operations", "deployment governance"),
    "search_relevance": ("result ordering", "relevance tuning"),
    "production_python": ("dependable Python services", "maintainable Python code"),
    "advisory_strategy": ("technology diligence", "advisory strategy"),
    "technical_leadership": ("architecture direction", "engineering stewardship"),
}

INDUSTRIES = ("healthcare", "financial services", "energy", "retail", "manufacturing", "technology")
ROLES = (
    "Data Scientist", "Machine Learning Engineer", "Search / Retrieval Engineer",
    "Data Engineer", "Solutions Architect", "AI Architect", "Engineering Manager",
    "Technical Lead", "Principal Engineer", "Research Scientist", "Consultant",
    "Domain Specialist", "Head of AI",
)
ROLE_SENIORITY = {
    "Data Scientist": "mid", "Machine Learning Engineer": "senior",
    "Search / Retrieval Engineer": "senior", "Data Engineer": "mid",
    "Solutions Architect": "principal", "AI Architect": "principal",
    "Engineering Manager": "principal", "Technical Lead": "senior",
    "Principal Engineer": "principal", "Research Scientist": "senior",
    "Consultant": "senior", "Domain Specialist": "mid", "Head of AI": "principal",
}
LOCATIONS = ("Portugal", "United Kingdom", "Spain", "Poland", "Germany", "Netherlands")
EMPLOYERS = (("org-northstar", "Northstar Health", "employer"), ("org-atlas", "Atlas Financial", "employer"), ("org-meridian", "Meridian Energy", "employer"), ("org-nova", "Nova Systems", "employer"), ("org-orion", "Orion Retail", "employer"))
CLIENTS = (("client-cairn", "Cairn Public Health", "public_sector"), ("client-verdant", "Verdant Mobility", "enterprise"), ("client-lumen", "Lumen Markets", "enterprise"), ("client-harbour", "Harbour Foods", "enterprise"), ("client-arc", "Arc Grid Services", "enterprise"))


def _concepts_for(index: int) -> list[str]:
    primary = CANONICAL_CONCEPTS[index % len(CANONICAL_CONCEPTS)]
    secondary = CANONICAL_CONCEPTS[(index * 5 + 3) % len(CANONICAL_CONCEPTS)]
    tertiary = CANONICAL_CONCEPTS[(index * 7 + 6) % len(CANONICAL_CONCEPTS)]
    return list(dict.fromkeys((primary, secondary, tertiary, "production_python")))


class V2DocumentProfileGenerator:
    """Generate profiles from canonical truth using document-only language."""

    def __init__(self, *, seed: int = 7301) -> None:
        self.seed = seed
        self.rng = Random(seed)

    def generate(self, index: int) -> V2ExpertProfile:
        rng = Random(self.seed * 100_003 + index * 97)
        expert_id = f"expert-v2-{index + 1:05d}"
        concepts = _concepts_for(index)
        industry = INDUSTRIES[(index * 3 + 1) % len(INDUSTRIES)]
        role = ROLES[index % len(ROLES)]
        location = LOCATIONS[(index * 7 + 1) % len(LOCATIONS)]
        employer_id, employer_name, _ = EMPLOYERS[(index * 11 + 1) % len(EMPLOYERS)]
        client_id, client_name, client_type = CLIENTS[(index * 13 + 2) % len(CLIENTS)]
        seniority = ROLE_SENIORITY[role]
        year_ranges = {"mid": (5, 8), "senior": (9, 15), "principal": (16, 25)}
        lo, hi = year_ranges[seniority]
        years = lo + ((index * 7) % (hi - lo + 1))
        start = date(2013 + index % 8, 1 + index % 6, 1)
        end = None if index % 7 == 0 else date(2020 + index % 5, 6 + index % 6, 1)
        project_start = date(max(start.year + 2, 2018 + index % 4), 2 + index % 8, 1)
        if end:
            # Keep delivery evidence inside the employment interval. Short
            # historical tenures use a compact project window rather than
            # inventing an out-of-period engagement.
            project_start = min(project_start, end - timedelta(days=180))
            project_start = max(project_start, start + timedelta(days=30))
            if project_start >= end:
                project_start = start
        project_end = project_start + timedelta(days=300 + (index % 5) * 90)
        if end and project_end > end:
            project_end = end
        if project_end <= project_start:
            project_end = project_start + timedelta(days=180)
        style = ("career_summary", "project_led", "concise_profile", "capability_focus", "advisory_profile", "role_history", "achievement_led", "evidence_first", "sparse_cv")[index % 9]
        verbosity = ("brief", "standard", "detailed")[(index * 3) % 3]
        surface = [DOCUMENT_SURFACES[c][rng.randrange(len(DOCUMENT_SURFACES[c]))] for c in concepts]
        headline = self._headline(style, role, surface[0], industry, rng)
        summary = self._summary(style, years, industry, role, surface, client_name, verbosity, rng, index, project_start, project_end)
        technology = surface[0]
        evidence: list[V2Evidence] = []
        employment_eid = f"ev-{index:05d}-employment"
        project_eid = f"ev-{index:05d}-project"
        skill_eid = f"ev-{index:05d}-skill"
        evidence.extend([
            V2Evidence(evidence_id=employment_eid, evidence_kind="employer_relationship", source_id=expert_id, text_span=employer_name, subject_id=expert_id, object_id=employer_id),
            V2Evidence(evidence_id=project_eid, evidence_kind="hands_on_delivery", source_id=expert_id, text_span=summary, subject_id=expert_id, object_id=f"project-{index:05d}"),
            V2Evidence(evidence_id=skill_eid, evidence_kind="skill_mention", source_id=expert_id, text_span=technology, subject_id=expert_id, object_id=concepts[0]),
        ])
        if index % 3 == 0:
            evidence.append(V2Evidence(evidence_id=f"ev-{index:05d}-advisory", evidence_kind="advisory_exposure", source_id=expert_id, text_span="advisory exposure", subject_id=expert_id, object_id=client_id))
        project = V2Project(project_id=f"project-{index:05d}", title=f"{industry.title()} discovery programme", client_id=client_id, client_name=client_name, client_type=client_type, industry=industry, role=role, technologies=[concepts[0], concepts[1]], canonical_concepts=concepts[:3], start_date=project_start, end_date=project_end, delivery_level="hands_on" if index % 4 else "technical_lead", evidence_ids=[project_eid])
        employment = V2Employment(organization_id=employer_id, organization_name=employer_name, role=role, industry=industry, start_date=start, end_date=end, current=end is None, evidence_ids=[employment_eid])
        relationships = [
            V2Relationship(edge_id=f"edge-{index:05d}-work", subject_id=expert_id, predicate="works_at", object_id=employer_id, object_type="employer", valid_from=start, valid_to=end, evidence_ids=[employment_eid]),
            V2Relationship(edge_id=f"edge-{index:05d}-delivery", subject_id=expert_id, predicate="delivered_for", object_id=client_id, object_type="client", valid_from=project_start, valid_to=project_end, evidence_ids=[project_eid]),
            V2Relationship(edge_id=f"edge-{index:05d}-project", subject_id=expert_id, predicate="has_project", object_id=project.project_id, object_type="project", valid_from=project_start, valid_to=project_end, evidence_ids=[project_eid]),
            V2Relationship(edge_id=f"edge-{index:05d}-industry", subject_id=expert_id, predicate="in_industry", object_id=industry, object_type="industry", evidence_ids=[project_eid]),
            V2Relationship(edge_id=f"edge-{index:05d}-location", subject_id=expert_id, predicate="located_in", object_id=location, object_type="location", evidence_ids=[employment_eid]),
        ]
        if index % 3 == 0:
            relationships.append(V2Relationship(edge_id=f"edge-{index:05d}-advisory", subject_id=expert_id, predicate="advised", object_id=client_id, object_type="client", valid_from=project_start, valid_to=project_end, evidence_ids=[f"ev-{index:05d}-advisory"]))
        profile = V2ExpertProfile(
            expert_id=expert_id, display_name=f"Expert {index + 1:05d}", headline=headline, summary=summary,
            canonical_concepts=concepts, skills=[surface[0], surface[-1], "ranking quality"], industries=[industry],
            technologies=[technology, surface[1]], roles=[role], seniority=seniority, employers=[employment], projects=[project],
            locations=[location], languages=["English", "Portuguese" if location == "Portugal" else "German"], certifications=["Cloud Architecture"] if index % 6 == 0 else [],
            advisory_areas=["technology advisory"] if index % 3 == 0 else [], relationships=relationships, evidence=evidence,
            years_experience=years, current_role=end is None, narrative_style=style, opening_pattern=style, verbosity_band=verbosity,
        )
        profile.search_document = self._projection(profile)
        return profile

    @staticmethod
    def _headline(style: str, role: str, surface: str, industry: str, rng: Random) -> str:
        variants = {
            "career_summary": f"{role}; {surface} in {industry}",
            "project_led": f"{role} delivering {surface} for {industry}",
            "concise_profile": f"{role} | {surface}",
            "capability_focus": f"{role} focused on {surface} in {industry}",
            "advisory_profile": f"{role} and technology adviser across {industry}",
            "role_history": f"{role} with a {industry} career history",
            "achievement_led": f"{role} improving {surface} for {industry}",
            "evidence_first": f"{role} with documented {surface} delivery",
            "sparse_cv": f"{role} — {surface}",
        }
        return variants[style]

    @staticmethod
    def _summary(style: str, years: int, industry: str, role: str, surfaces: list[str], client: str, verbosity: str, rng: Random, index: int, project_start: date, project_end: date) -> str:
        milestones = ("search quality reviews", "migration planning", "operational handover", "stakeholder workshops", "production readiness", "data-governance mapping", "relevance baselines", "service instrumentation", "model-risk review", "delivery coaching", "architecture options", "pilot design")
        months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
        workstreams = ("discovery", "platform", "quality", "delivery", "data", "governance", "operations", "integration", "analytics", "enablement", "architecture", "migration", "risk", "search", "model", "service", "product", "portfolio", "research", "adoption")
        month = months[index % 12]
        milestone = milestones[index % len(milestones)]
        workstream = workstreams[index % len(workstreams)]
        if style == "career_summary":
            text = f"{role} with {years} years across {industry}; focus areas include {surfaces[0]} and {surfaces[1]}."
        elif style == "project_led":
            text = f"For {client}, delivered {surfaces[0]} during a {workstream} engagement. The wider practice also covers {surfaces[1]} and {surfaces[2]}."
        elif style == "concise_profile":
            text = f"{role}. {surfaces[0]}; {surfaces[1]}. {industry.title()} delivery experience."
        elif style == "capability_focus":
            text = f"Focus areas: {surfaces[0]}, {surfaces[1]}, and {surfaces[2]}. Applies them to {industry} teams with {milestone}."
        elif style == "advisory_profile":
            text = f"Advises {client} and {industry} stakeholders on {surfaces[0]}. Delivery evidence also covers {surfaces[1]} and {surfaces[2]}."
        elif style == "role_history":
            text = f"Career record: {role} in {industry}, with {years} years of practice. Recent work includes {surfaces[0]} and {milestone}."
        elif style == "achievement_led":
            text = f"Improved {surfaces[0]} for {client}; the engagement ran from {project_start.isoformat()} to {project_end.isoformat()}. Related capabilities include {surfaces[1]}."
        elif style == "evidence_first":
            text = f"Recorded delivery: {surfaces[0]} for {client} ({project_start.isoformat()}–{project_end.isoformat()}). Role context: {role} in {industry}."
        else:
            text = f"{role}; {industry}; {surfaces[0]}; {surfaces[1]}."
        if verbosity == "detailed":
            text += f" {milestone.capitalize()} was part of the {workstream} workstream, first recorded in {month} {2014 + index % 9}."
        return text

    @staticmethod
    def _projection(profile: V2ExpertProfile) -> dict[str, Any]:
        return {
            "expert_id": profile.expert_id, "display_name": profile.display_name, "headline": profile.headline,
            "summary": profile.summary, "skills": profile.skills, "industries": profile.industries,
            "technologies": profile.technologies, "roles": profile.roles, "locations": profile.locations,
            "project_titles": [p.title for p in profile.projects], "project_clients": [p.client_name for p in profile.projects],
            "project_descriptions": [profile.summary for _ in profile.projects], "employer_names": [e.organization_name for e in profile.employers],
            "relationship_predicates": [r.predicate for r in profile.relationships], "evidence_kinds": [e.evidence_kind for e in profile.evidence],
        }


class V2QueryGenerator:
    """Generate query surfaces independently from document wording."""

    def __init__(self, *, seed: int = 9137) -> None:
        self.seed = seed
        self.rng = Random(seed)

    def generate(self, count: int = 40) -> tuple[V2Query, ...]:
        if count < 30 or count > 120:
            raise ValueError("v2 pilot query count must be between 30 and 40")
        categories = list(QueryCategory)
        queries: list[V2Query] = []
        for i in range(count):
            category = categories[i % len(categories)]
            concept = CANONICAL_CONCEPTS[(i * 5 + 1) % len(CANONICAL_CONCEPTS)]
            surface = QUERY_SURFACES[concept][i % len(QUERY_SURFACES[concept])]
            required = [concept]
            optional: list[str] = []
            prohibited: list[str] = []
            industry = INDUSTRIES[(i * 3 + 1) % len(INDUSTRIES)]
            role = ROLES[(i + 2) % len(ROLES)]
            seniority = ROLE_SENIORITY[role]
            relationship: list[str] = []
            evidence: list[str] = []
            organization = None
            role_required: list[str] = []
            seniority_required: list[str] = []
            semantic_bucket: Literal["exact", "partial", "semantic", "low_overlap"] = "exact"
            hard_negative_type = None
            temporal_start = temporal_end = None
            if category is QueryCategory.skill_industry:
                surface = f"{surface} for {industry} practitioners"
            elif category is QueryCategory.organization:
                organization = EMPLOYERS[i % len(EMPLOYERS)][1]
                relationship = ["works_at"]
                surface = f"Find someone who worked at {organization and organization} with {surface}"
            elif category is QueryCategory.seniority_role:
                role_required = [role]
                seniority_required = [seniority]
                surface = f"{seniority}-level {role.lower()} demonstrating {surface}"
            elif category is QueryCategory.delivery_project:
                relationship = ["delivered_for"]
                evidence = ["hands_on_delivery"]
                surface = f"Find a practitioner with hands-on project delivery in {surface}"
            elif category is QueryCategory.multi_constraint:
                required = [concept, "technical_leadership"]
                optional = ["production_python"]
                semantic_bucket = "partial"
                surface = f"{surface} for {industry} teams; technical leadership required"
            elif category is QueryCategory.negative_constraint:
                prohibited = ["financial_risk"]
                surface = f"{surface}, explicitly excluding regulated finance work"
            elif category is QueryCategory.temporal:
                evidence = ["hands_on_delivery"]
                surface = f"{surface} delivered between 2021 and 2025"
            elif category is QueryCategory.semantic_paraphrase:
                semantic_bucket = "semantic"
            elif category is QueryCategory.hard_negative:
                hard_negative_type = ("wrong_relationship", "advisory_only", "outside_window", "missing_skill")[(i // len(categories)) % 4]
                relationship = ["works_at"] if hard_negative_type == "wrong_relationship" else (["advised"] if hard_negative_type == "advisory_only" else [])
                organization = "Unavailable Organisation" if hard_negative_type == "wrong_relationship" else None
                evidence = ["hands_on_delivery"] if hard_negative_type == "advisory_only" else []
                if hard_negative_type == "outside_window":
                    temporal_start, temporal_end = date(2028, 1, 1), date(2030, 12, 31)
                else:
                    temporal_start = temporal_end = None
                if hard_negative_type == "missing_skill":
                    optional = [CANONICAL_CONCEPTS[(i * 7 + 4) % len(CANONICAL_CONCEPTS)]]
                surface = f"{surface} with the requested delivery evidence, not an adjacent match"
            elif category is QueryCategory.exact_skill:
                semantic_bucket = "exact"
            if category is QueryCategory.semantic_paraphrase or (category is QueryCategory.exact_skill and i in {20, 30}):
                semantic_bucket = "low_overlap"
                surface = ("experience improving how users find relevant technical knowledge" if concept == "search_relevance" else f"experience applying {surface} in real delivery")
            queries.append(V2Query(query_id=f"v2-q-{i + 1:03d}", query_text=surface, category=category, canonical_required=required, canonical_optional=optional, required_capabilities=["technical_leadership"] if category is QueryCategory.multi_constraint else [], canonical_prohibited=prohibited, industry_required=[industry] if category in {QueryCategory.skill_industry, QueryCategory.multi_constraint} else [], organization_required=organization, relationship_required=relationship, evidence_required=evidence, role_required=role_required, seniority_required=seniority_required, semantic_bucket=semantic_bucket, hard_negative_type=hard_negative_type, temporal_start=temporal_start if category is QueryCategory.hard_negative else (date(2021, 1, 1) if category is QueryCategory.temporal else None), temporal_end=temporal_end if category is QueryCategory.hard_negative else (date(2025, 12, 31) if category is QueryCategory.temporal else None), expected_signals=[category.value]))
        return tuple(queries)


class V2JudgementBuilder:
    """Build draft Gold/Silver judgements from canonical truth only."""

    def build(self, queries: Iterable[V2Query], profiles: Iterable[V2ExpertProfile]) -> tuple[V2Judgement, ...]:
        output: list[V2Judgement] = []
        for query in queries:
            for profile in profiles:
                matched = [c for c in query.canonical_required if c in profile.canonical_concepts]
                optional = [c for c in query.canonical_optional if c in profile.canonical_concepts]
                violated = [c for c in query.canonical_prohibited if c in profile.canonical_concepts]
                evidence = [e.evidence_id for e in profile.evidence if e.object_id in matched or e.object_id in {p.project_id for p in profile.projects}]
                missing_requirements: list[str] = []
                industry_ok = not query.industry_required or any(i in profile.industries for i in query.industry_required)
                role_ok = not query.role_required or any(r in profile.roles for r in query.role_required)
                seniority_ok = not query.seniority_required or profile.seniority in query.seniority_required
                relationship_ok = not query.relationship_required or any(r.predicate in query.relationship_required for r in profile.relationships)
                evidence_ok = not query.evidence_required or any(e.evidence_kind in query.evidence_required for e in profile.evidence)
                organization_ok = not query.organization_required or any(e.organization_name == query.organization_required for e in profile.employers)
                temporal_ok = True
                if query.temporal_start:
                    temporal_ok = any(p.end_date >= query.temporal_start and p.start_date <= (query.temporal_end or date.max) for p in profile.projects)
                if not industry_ok: missing_requirements.append("industry")
                if not role_ok: missing_requirements.append("role")
                if not seniority_ok: missing_requirements.append("seniority")
                if not relationship_ok: missing_requirements.append("relationship")
                if not evidence_ok: missing_requirements.append("evidence")
                if not organization_ok: missing_requirements.append("organization")
                if violated or not temporal_ok:
                    grade: Literal[0, 1, 2, 3] = 0
                    codes = ["prohibited_concept"] if violated else ["outside_temporal_window"]
                elif len(matched) == len(query.canonical_required) and industry_ok and role_ok and seniority_ok and relationship_ok and evidence_ok and organization_ok:
                    grade = 2 if (query.canonical_optional and len(optional) < len(query.canonical_optional)) or query.semantic_bucket == "semantic" else 3
                    codes = ["canonical_match", "evidence_backed" if grade == 3 else "incomplete_optional_requirement"]
                elif matched and missing_requirements:
                    grade = 1
                    codes = ["partial_canonical_match", "missing_structured_requirement"]
                elif matched:
                    grade = 1
                    codes = ["partial_canonical_match"]
                else:
                    grade = 0
                    codes = ["no_canonical_match"]
                output.append(V2Judgement(query_id=query.query_id, expert_id=profile.expert_id, grade=grade, matched_concepts=matched + optional, missing_concepts=[c for c in query.canonical_required if c not in matched], violated_concepts=violated, evidence_ids=evidence, rationale_codes=codes, missing_requirements=missing_requirements, review_status="draft_gold_structured_audit" if grade >= 2 else "draft_silver_rule_assisted"))
        return tuple(output)


def pipeline_boundaries(document_seed: int, query_seed: int) -> dict[str, Any]:
    return {"document_pipeline": {"seed": document_seed, "surface_lexicon_version": V2_SURFACE_LEXICON_VERSION}, "query_pipeline": {"seed": query_seed, "surface_lexicon_version": "query-surface-lexicon-v2-separated"}, "judgement_pipeline": {"inputs": ["canonical ontology IDs", "relationships", "temporal records", "evidence records"], "forbidden_inputs": ["search_document", "query_text", "retrieval_results"]}, "shared_inputs": ["canonical ontology IDs"]}


def _canonical_profiles(profiles: Iterable[V2ExpertProfile]) -> list[dict[str, Any]]:
    return [p.model_dump(mode="json") for p in profiles]


def build_v2_pilot(output_root: str | Path, *, size: int = 750, seed: int = 7301, query_count: int = 40, query_seed: int = 9137, dataset_version: str = V2_DATASET_VERSION, generator_version: str = V2_GENERATOR_VERSION) -> V2Manifest:
    if not 500 <= size <= 10000:
        raise ValueError("v2 dataset size must be between 500 and 10000")
    root = Path(output_root)
    (root / "knowledge").mkdir(parents=True, exist_ok=True)
    (root / "queries").mkdir(parents=True, exist_ok=True)
    (root / "judgements").mkdir(parents=True, exist_ok=True)
    profiles = tuple(V2DocumentProfileGenerator(seed=seed).generate(i) for i in range(size))
    queries = V2QueryGenerator(seed=query_seed).generate(query_count)
    judgements = V2JudgementBuilder().build(queries, profiles)
    profile_payload = _canonical_profiles(profiles)
    checksum = _sha(profile_payload)
    (root / "knowledge" / "experts.json").write_text(json.dumps(profile_payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (root / "queries" / "queries.json").write_text(json.dumps([q.model_dump(mode="json") for q in queries], indent=2, sort_keys=True, default=str), encoding="utf-8")
    (root / "judgements" / "judgements.json").write_text(json.dumps([j.model_dump(mode="json") for j in judgements], indent=2, sort_keys=True, default=str), encoding="utf-8")
    manifest = V2Manifest(record_count=len(profiles), query_count=len(queries), seed=seed, document_seed=seed, query_seed=query_seed, checksum=checksum, dataset_version=dataset_version, generator_version=generator_version)
    (root / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def _length_stats(texts: list[str]) -> dict[str, float]:
    lengths = [len(_tokens(t)) for t in texts]
    return {"mean": round(mean(lengths), 3), "p50": float(median(lengths)), "p95": float(sorted(lengths)[min(len(lengths) - 1, math.ceil(len(lengths) * 0.95) - 1)])}


def _surface_metrics(documents: list[str], queries: list[str]) -> dict[str, float]:
    doc_tokens = [_tokens(t) for t in documents]
    query_tokens = [_tokens(t) for t in queries]
    all_tokens = [token for row in doc_tokens for token in row]
    grams = [" ".join(row[i:i + 2]) for row in doc_tokens for i in range(max(0, len(row) - 1))]
    overlaps = []
    for query in query_tokens:
        qset = set(query)
        overlaps.append(len(qset & set(token for row in doc_tokens for token in row)) / max(1, len(qset)))
    document_trigrams = {" ".join(row[i:i + 3]) for row in doc_tokens for i in range(max(0, len(row) - 2))}
    query_trigrams = {" ".join(row[i:i + 3]) for row in query_tokens for i in range(max(0, len(row) - 2))}
    # Surface overlap intentionally measures reusable three-token phrases, not
    # generic words such as "expert" or "delivery".  This exposes templated
    # leakage while remaining comparable with the v1 pilot.
    phrase_overlap = len(document_trigrams & query_trigrams) / max(1, len(query_trigrams))
    return {"lexical_diversity": round(len(set(all_tokens)) / max(1, len(all_tokens)), 6), "unique_bigram_ratio": round(len(set(grams)) / max(1, len(grams)), 6), "query_document_surface_overlap": round(phrase_overlap, 6), "query_document_token_overlap": round(mean(overlaps), 6)}


def validate_query_contracts(queries: Iterable[V2Query]) -> dict[str, Any]:
    """Validate that natural query language and structured constraints agree."""
    rows: list[dict[str, Any]] = []
    for query in queries:
        text = query.query_text.lower()
        errors: list[str] = []
        if query.category is QueryCategory.multi_constraint:
            for industry in query.industry_required:
                if f"for {industry}" not in text and f"in {industry}" not in text:
                    errors.append("required industry missing from query text")
            for capability in query.required_capabilities:
                if capability == "technical_leadership" and "technical leadership required" not in text:
                    errors.append("required technical leadership is not stated as required")
            if "technical_leadership" not in query.canonical_required:
                errors.append("required technical leadership missing from canonical_required")
            if "technical_leadership" in query.canonical_optional:
                errors.append("technical leadership incorrectly marked optional")
        if query.category is QueryCategory.organization:
            if not query.organization_required or not query.relationship_required or "worked at" not in text:
                errors.append("organization relationship contract mismatch")
        if query.category is QueryCategory.seniority_role:
            if not query.role_required or not query.seniority_required or not any(s in text for s in query.seniority_required):
                errors.append("role/seniority contract mismatch")
        if query.category is QueryCategory.skill_industry and not query.industry_required:
            errors.append("skill_industry lacks industry constraint")
        if query.category is QueryCategory.delivery_project and not (query.relationship_required or query.evidence_required):
            errors.append("delivery_project lacks delivery evidence contract")
        if query.category is QueryCategory.temporal and not (query.temporal_start and query.temporal_end):
            errors.append("temporal query lacks complete window")
        if query.category is QueryCategory.negative_constraint and not query.canonical_prohibited:
            errors.append("negative query lacks prohibited constraint")
        rows.append({"query_id": query.query_id, "category": query.category.value, "valid": not errors, "errors": errors})
    return {"valid": all(row["valid"] for row in rows), "query_count": len(rows), "invalid_query_ids": [row["query_id"] for row in rows if not row["valid"]], "rows": rows}


def _hard_negative_metrics(queries: list[V2Query], profiles: list[V2ExpertProfile], judgements: list[V2Judgement]) -> dict[str, Any]:
    by_query = {q.query_id: q for q in queries}
    true_hard = 0
    hard_candidates = 0
    type_counts: Counter[str] = Counter()
    for judgement in judgements:
        query = by_query[judgement.query_id]
        if query.category is not QueryCategory.hard_negative:
            continue
        hard_candidates += 1
        # A true hard negative is a near-miss with canonical support plus a
        # structured failure (or a prohibited/temporal failure). Unrelated
        # grade-0 candidates are ordinary/easy negatives.
        near_miss = bool(judgement.matched_concepts) and bool(
            judgement.missing_requirements or judgement.violated_concepts or "outside_temporal_window" in judgement.rationale_codes
            or (query.hard_negative_type == "missing_skill" and judgement.missing_concepts)
        )
        if near_miss:
            true_hard += 1
            if query.hard_negative_type:
                type_counts[query.hard_negative_type] += 1
    total = len(judgements)
    negative = sum(j.grade == 0 for j in judgements)
    easy = negative - true_hard
    return {
        "negative_judgement_rate": round(negative / max(1, total), 6),
        "hard_negative_judgement_rate": round(true_hard / max(1, total), 6),
        "easy_negative_rate": round(easy / max(1, total), 6),
        "hard_negative_query_count": sum(q.category is QueryCategory.hard_negative for q in queries),
        "hard_negative_candidate_count": hard_candidates,
        "true_hard_negative_count": true_hard,
        "hard_negative_type_distribution": dict(type_counts),
        "denominators": {"negative_judgement_rate": "all judgements", "hard_negative_judgement_rate": "all judgements", "easy_negative_rate": "all judgements"},
        "legacy_density": round(sum(j.grade == 0 for j, q in zip(judgements, [queries[i // len(profiles)] for i in range(len(judgements))]) if q.category is QueryCategory.hard_negative) / max(1, sum(q.category is QueryCategory.hard_negative for q in queries) * len(profiles)), 6),
    }


def audit_v2_pilot(root: str | Path, *, v1_profiles: Iterable[Any] | None = None, v1_queries: Iterable[Any] | None = None) -> dict[str, Any]:
    root = Path(root)
    profiles = [V2ExpertProfile.model_validate(row) for row in json.loads((root / "knowledge" / "experts.json").read_text())]
    queries = [V2Query.model_validate(row) for row in json.loads((root / "queries" / "queries.json").read_text())]
    judgements = [V2Judgement.model_validate(row) for row in json.loads((root / "judgements" / "judgements.json").read_text())]
    docs = [f"{p.headline} {p.summary}" for p in profiles]
    normalized = [_normalized(p.summary) for p in profiles]
    duplicate_rate = 1 - len(set(normalized)) / max(1, len(normalized))
    # Use bounded three-shingle Jaccard rather than an expensive edit-distance
    # matrix.  This is deterministic, auditable, and scales to the 1K pilot.
    shingles = [set(" ".join(row[i:i + 3]) for i in range(max(0, len(row) - 2))) for row in (_tokens(x) for x in normalized)]
    near_pairs = 0
    for i in range(len(shingles)):
        for j in range(i + 1, len(shingles)):
            if not shingles[i] or not shingles[j]:
                continue
            if abs(len(shingles[i]) - len(shingles[j])) / max(len(shingles[i]), len(shingles[j])) > 0.35:
                continue
            union = len(shingles[i] | shingles[j])
            if union and len(shingles[i] & shingles[j]) / union >= 0.85:
                near_pairs += 1
    styles = Counter(p.narrative_style for p in profiles)
    role_counts = Counter(role for p in profiles for role in p.roles)
    seniority_counts = Counter(p.seniority for p in profiles)
    openings = Counter(p.opening_pattern for p in profiles)
    sentence_counts = Counter(max(1, p.summary.count(".") + p.summary.count("?")) for p in profiles)
    predicate_counts = Counter(edge.predicate for p in profiles for edge in p.relationships)
    invalid_temporal = sum(1 for p in profiles for e in p.employers if e.end_date and e.end_date < e.start_date) + sum(1 for p in profiles for x in p.projects if x.end_date <= x.start_date)
    projects_outside_employment = sum(1 for p in profiles for x in p.projects for e in p.employers if e.end_date and (x.start_date < e.start_date or x.end_date > e.end_date))
    evidence_coverage = sum(bool(j.evidence_ids) for j in judgements if j.grade >= 2) / max(1, sum(j.grade >= 2 for j in judgements))
    grade_counts = Counter(j.grade for j in judgements)
    category_counts = Counter(q.category.value for q in queries)
    query_buckets = Counter(q.semantic_bucket for q in queries)
    hard_negative_types = Counter(q.hard_negative_type for q in queries if q.hard_negative_type)
    query_contract_validation = validate_query_contracts(queries)
    hard_negative_metrics = _hard_negative_metrics(queries, profiles, judgements)
    category_semantics = {
        "organization_explicit_relationship": sum(bool(q.organization_required and q.relationship_required) for q in queries if q.category is QueryCategory.organization),
        "seniority_role_explicit": sum(bool(q.role_required and q.seniority_required) for q in queries if q.category is QueryCategory.seniority_role),
        "skill_industry_both": sum(bool(q.canonical_required and q.industry_required) for q in queries if q.category is QueryCategory.skill_industry),
        "delivery_explicit": sum(bool(q.evidence_required or q.relationship_required) for q in queries if q.category is QueryCategory.delivery_project),
        "temporal_explicit": sum(bool(q.temporal_start and q.temporal_end) for q in queries if q.category is QueryCategory.temporal),
        "negative_explicit": sum(bool(q.canonical_prohibited) for q in queries if q.category is QueryCategory.negative_constraint),
    }
    audit = {
        "identity": json.loads((root / "manifest.json").read_text()),
        "counts": {"profiles": len(profiles), "queries": len(queries), "judgements": len(judgements)},
        "duplicates": {"normalized_summary_duplicate_rate": round(duplicate_rate, 6), "near_duplicate_pair_count": near_pairs, "near_duplicate_pair_rate": round(near_pairs / max(1, len(profiles) * (len(profiles) - 1) / 2), 6)},
        "surface_metrics": _surface_metrics(docs, [q.query_text for q in queries]),
        "length_stats": {"documents": _length_stats(docs), "queries": _length_stats([q.query_text for q in queries])},
        "template_frequency": dict(styles),
        "role_distribution": dict(role_counts),
        "seniority_distribution": dict(seniority_counts),
        "narrative_family_distribution": dict(styles),
        "opening_pattern_distribution": dict(openings),
        "dominant_opening_pattern_frequency": round(max(openings.values()) / max(1, len(profiles)), 6),
        "sentence_count_distribution": dict(sentence_counts),
        "relationships": {"edge_count": sum(predicate_counts.values()), "by_predicate": dict(predicate_counts), "profiles_with_multiple_entity_types": sum(len({r.object_type for r in p.relationships}) >= 3 for p in profiles)},
        "temporal": {"profiles_with_temporal_records": sum(bool(p.employers or p.projects) for p in profiles), "invalid_records": invalid_temporal, "projects_outside_employment": projects_outside_employment, "current_profiles": sum(p.current_role for p in profiles)},
        "evidence": {"positive_judgement_evidence_coverage": round(evidence_coverage, 6), "evidence_kind_counts": dict(Counter(e.evidence_kind for p in profiles for e in p.evidence))},
        "hard_negatives": {**hard_negative_metrics, "types": dict(hard_negative_types)},
        "grades": dict(grade_counts), "categories": dict(category_counts),
        "query_semantic_buckets": dict(query_buckets),
        "category_semantic_validation": category_semantics,
        "query_contract_validation": query_contract_validation,
        "leakage_risk": ["controlled vocabulary remains a leakage risk", "templated synthetic language remains present", "Gold is structured audit evidence, not external human ground truth"],
        "invalid_record_count": invalid_temporal,
        "pipeline_boundaries": pipeline_boundaries(json.loads((root / "manifest.json").read_text())["document_seed"], json.loads((root / "manifest.json").read_text())["query_seed"]),
    }
    # A deterministic inspection sample is embedded in the audit for review and
    # provenance. Select one example of every grade before filling the sample.
    selected_judgements: list[V2Judgement] = []
    for grade in (3, 2, 1, 0):
        selected_judgements.extend([j for j in judgements if j.grade == grade][:2])
    selected_ids = {(j.query_id, j.expert_id) for j in selected_judgements}
    selected_judgements.extend(j for j in judgements if (j.query_id, j.expert_id) not in selected_ids)
    audit["manual_inspection"] = {
        "profiles": [p.model_dump(mode="json") for p in profiles[:20]],
        "queries": [q.model_dump(mode="json") for q in queries[:20]],
        "judgement_examples": [j.model_dump(mode="json") for j in selected_judgements[:20]],
        "grade_coverage": sorted({j.grade for j in selected_judgements[:20]}),
        "query_categories": sorted({q.category.value for q in queries[:20]}),
    }
    if v1_profiles is not None and v1_queries is not None:
        v1_docs = [f"{p.headline} {p.summary}" for p in v1_profiles]
        v1_surface = _surface_metrics(v1_docs, [q.query_text for q in v1_queries])
        audit["v1_comparison"] = {"surface_metrics": v1_surface, "v2_lower_overlap": audit["surface_metrics"]["query_document_surface_overlap"] < v1_surface["query_document_surface_overlap"], "v2_lower_lexical_diversity_is_not_required": True}
    return audit


def write_audit(root: str | Path, audit: dict[str, Any]) -> None:
    root = Path(root)
    (root / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True, default=str), encoding="utf-8")
    identity = audit["identity"]
    lines = [f"# Dataset v2 Pilot Audit ({identity['dataset_id']})", "", "Status: pilot quality gate; not production-realistic.", "", "## Counts", "", f"- Profiles: {audit['counts']['profiles']}", f"- Queries: {audit['counts']['queries']}", f"- Judgements: {audit['counts']['judgements']}", "", "## Diversity and leakage diagnostics", "", f"- Summary duplicate rate: {audit['duplicates']['normalized_summary_duplicate_rate']:.2%}", f"- Near-duplicate pair rate: {audit['duplicates']['near_duplicate_pair_rate']:.2%}", f"- Lexical diversity: {audit['surface_metrics']['lexical_diversity']:.4f}", f"- Unique bigram ratio: {audit['surface_metrics']['unique_bigram_ratio']:.4f}", f"- Query/document surface overlap: {audit['surface_metrics']['query_document_surface_overlap']:.4f}", "", "## Integrity", "", f"- Invalid temporal records: {audit['temporal']['invalid_records']}", f"- Positive judgement evidence coverage: {audit['evidence']['positive_judgement_evidence_coverage']:.2%}", f"- v2 lower surface overlap than v1 pilot: {audit.get('v1_comparison', {}).get('v2_lower_overlap', 'not compared')}", "", "## Limitations", "", "This is a controlled synthetic relevance benchmark. It contains templated synthetic language and controlled-vocabulary leakage risk. Gold is an independent structured audit, not external human ground truth. It must not be generalized to natural expert-network data."]
    (root / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


__all__ = ["V2Evidence", "V2Relationship", "V2Employment", "V2Project", "V2ExpertProfile", "V2Query", "V2Judgement", "V2Manifest", "V2DocumentProfileGenerator", "V2QueryGenerator", "V2JudgementBuilder", "build_v2_pilot", "audit_v2_pilot", "write_audit", "pipeline_boundaries", "validate_query_contracts"]
