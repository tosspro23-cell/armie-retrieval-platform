"""ARMIE Retrieval Platform reference implementation."""

__version__ = "0.5.1"

from .models.domain import EvaluationResult, ExecutionObservation, Policy, Query, RetrievalPlan, RetrievalResult, ResultItem
from .runtime import RetrievalRuntime
from .contracts import Constraint, ConstraintPolicy, RetrievalContract, validate_contract

__all__ = ["__version__", "EvaluationResult", "ExecutionObservation", "Policy", "Query", "RetrievalPlan", "RetrievalResult", "ResultItem", "RetrievalRuntime", "Constraint", "ConstraintPolicy", "RetrievalContract", "validate_contract"]
