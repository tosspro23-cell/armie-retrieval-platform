"""Gate 1 candidate-interpretation schema and deterministic evaluator.

This package intentionally contains no natural-language extractor and no
runtime execution path.  It represents and evaluates untrusted candidate
interpretations before any future confirmation/validation boundary.
"""

from .models import (
    CANDIDATE_INTERPRETATION_SCHEMA,
    CandidateConstraint,
    CandidateInterpretation,
    InterpretationState,
    Polarity,
    SupportState,
)
from .evaluator import EvaluationResult, evaluate_interpretation
from .serialization import canonical_jsonl, fingerprint_records
from .extractors import (CascadeExtractorV2, ExtractionResult, HybridExtractor,
                         OllamaStructuredExtractor, OllamaStructuredExtractorV2,
                         RuleExtractor, RuleExtractorV3)
from .staged import (
    STAGED_SCHEMA,
    SemanticRole,
    StagedResult,
    staged_extract,
    ModelAssistedStagedExtractor,
)
from .stage_evaluator import StageGold, role_metrics
from .clarification import (
    CLARIFICATION_ITEM_SCHEMA, CLARIFICATION_RESOLUTION_SCHEMA,
    ClarificationItem, ClarificationResolution, ClarificationStatus,
    ClarificationType, InterpretationSession, apply_resolution, confirm,
    question_for, start_session, validate_contract,
)

__all__ = [
    "CANDIDATE_INTERPRETATION_SCHEMA",
    "CandidateConstraint",
    "CandidateInterpretation",
    "EvaluationResult",
    "InterpretationState",
    "Polarity",
    "SupportState",
    "evaluate_interpretation",
    "canonical_jsonl",
    "fingerprint_records",
    "ExtractionResult",
    "RuleExtractor",
    "OllamaStructuredExtractor",
    "HybridExtractor",
    "RuleExtractorV3",
    "OllamaStructuredExtractorV2",
    "CascadeExtractorV2",
    "STAGED_SCHEMA",
    "SemanticRole",
    "StagedResult",
    "staged_extract",
    "ModelAssistedStagedExtractor",
    "StageGold",
    "role_metrics",
    "CLARIFICATION_ITEM_SCHEMA", "CLARIFICATION_RESOLUTION_SCHEMA",
    "ClarificationItem", "ClarificationResolution", "ClarificationStatus",
    "ClarificationType", "InterpretationSession", "apply_resolution", "confirm",
    "question_for", "start_session", "validate_contract",
]
