"""Reproducible benchmark manifests, profiles, metrics, and failure reports."""

from .engine import BenchmarkProfile, ExperimentManifest, default_profiles, gate4_profiles, run_profile
from .failures import FailureCode, classify_failure
from .metrics import graded_metrics
from .reports import render_report
from .relevance import GOLD_COUNTS, audit_dataset, audit_tier, benchmark_metrics, grade_map, independent_judgement, select_gold_queries

__all__ = ["BenchmarkProfile", "ExperimentManifest", "FailureCode", "GOLD_COUNTS", "audit_dataset", "audit_tier", "benchmark_metrics", "classify_failure", "default_profiles", "gate4_profiles", "grade_map", "graded_metrics", "independent_judgement", "render_report", "run_profile", "select_gold_queries"]
