"""
Zecpath-AI: Technical Skill Scoring Models & Evaluation Schemas
==============================================================
Pydantic schemas and dataclasses defining the 4-factor scoring parameters,
rubric weights per question type, shallow vs deep detection metrics,
difficulty normalization models, and explainable evaluation reporting.

Curriculum Reference: Day 47 - Technical Skill Scoring Model
"""

from typing import List, Dict, Optional, Any, Set
from enum import Enum
from pydantic import BaseModel, Field
import time


# ==============================================================================
# 1. CORE ENUMS & TAXONOMIES
# ==============================================================================

class ScoringParameter(str, Enum):
    """The four foundational technical evaluation parameters."""
    ACCURACY = "ACCURACY"                           # Factual correctness, API/syntax validity
    DEPTH = "DEPTH"                                 # Internal mechanics, memory, execution layers
    LOGICAL_REASONING = "LOGICAL_REASONING"         # Algorithmic deduction, trade-off defense, complexity
    REAL_WORLD_APPLICABILITY = "REAL_WORLD_APPLICABILITY"  # Production constraints, incidents, scaling limits


class AnswerDepthClassification(str, Enum):
    """Classification of technical answer substance."""
    SHALLOW_SURFACE = "SHALLOW_SURFACE"             # Buzzwords, circular logic, no mechanics
    MODERATE_FOUNDATIONAL = "MODERATE_FOUNDATIONAL" # Correct basics, limited edge case awareness
    DEEP_ANALYTICAL = "DEEP_ANALYTICAL"             # Explains internal layers, trade-offs, mechanics
    EXPERT_ARCHITECTURAL = "EXPERT_ARCHITECTURAL"   # Comprehensive distributed design, failure triage


class SkillProficiencyLevel(str, Enum):
    """Graded proficiency tier per skill domain."""
    NOVICE = "NOVICE"                               # 0.0 - 39.9%
    COMPETENT = "COMPETENT"                         # 40.0 - 59.9%
    PROFICIENT = "PROFICIENT"                       # 60.0 - 74.9%
    ADVANCED = "ADVANCED"                           # 75.0 - 89.9%
    EXPERT = "EXPERT"                               # 90.0 - 100.0%


# ==============================================================================
# 2. RUBRIC CONFIGURATION PER QUESTION CATEGORY
# ==============================================================================

class QuestionTypeRubric(BaseModel):
    """Calibrated weight distribution across the 4 parameters for a question type."""
    accuracy_weight: float = Field(..., ge=0.0, le=1.0)
    depth_weight: float = Field(..., ge=0.0, le=1.0)
    logical_reasoning_weight: float = Field(..., ge=0.0, le=1.0)
    real_world_applicability_weight: float = Field(..., ge=0.0, le=1.0)

    def model_post_init(self, __context: Any) -> None:
        total = round(
            self.accuracy_weight +
            self.depth_weight +
            self.logical_reasoning_weight +
            self.real_world_applicability_weight,
            4
        )
        if total != 1.0:
            raise ValueError(f"Rubric weights must sum to 1.0, got {total}")


# Standard rubrics calibrated per question type
QUESTION_TYPE_RUBRICS: Dict[str, QuestionTypeRubric] = {
    # Conceptual: focuses on theoretical correctness & runtime depth
    "CONCEPTUAL": QuestionTypeRubric(
        accuracy_weight=0.40,
        depth_weight=0.35,
        logical_reasoning_weight=0.15,
        real_world_applicability_weight=0.10,
    ),
    # Experience-based: focuses on production application & past trade-offs
    "EXPERIENCE_BASED": QuestionTypeRubric(
        accuracy_weight=0.15,
        depth_weight=0.25,
        logical_reasoning_weight=0.25,
        real_world_applicability_weight=0.35,
    ),
    # Scenario-based: focuses on incident triage, root-cause deduction, production handling
    "SCENARIO_BASED": QuestionTypeRubric(
        accuracy_weight=0.15,
        depth_weight=0.20,
        logical_reasoning_weight=0.30,
        real_world_applicability_weight=0.35,
    ),
    # System Design: focuses on architecture logic, scalability trade-offs, failure resilience
    "SYSTEM_DESIGN": QuestionTypeRubric(
        accuracy_weight=0.10,
        depth_weight=0.25,
        logical_reasoning_weight=0.35,
        real_world_applicability_weight=0.30,
    ),
    # Introduction & Wrap-up: balanced baseline
    "INTRODUCTION": QuestionTypeRubric(
        accuracy_weight=0.25,
        depth_weight=0.25,
        logical_reasoning_weight=0.25,
        real_world_applicability_weight=0.25,
    ),
    "WRAP_UP": QuestionTypeRubric(
        accuracy_weight=0.25,
        depth_weight=0.25,
        logical_reasoning_weight=0.25,
        real_world_applicability_weight=0.25,
    ),
}


# ==============================================================================
# 3. DETAILED TURN SCORING & SHALLOW DETECTION
# ==============================================================================

class ShallowAnswerDiagnostics(BaseModel):
    """Analysis of superficial vs deep answer signals."""
    depth_classification: AnswerDepthClassification
    depth_index: float = Field(..., ge=0.0, le=1.0, description="Quantitative depth score")
    buzzword_density: float = Field(..., ge=0.0, le=1.0, description="Ratio of buzzwords to technical mechanics")
    detected_buzzwords_without_context: List[str] = Field(default_factory=list)
    mechanisms_explained: List[str] = Field(default_factory=list)
    tradeoffs_defended: List[str] = Field(default_factory=list)
    concrete_metrics_cited: List[str] = Field(default_factory=list)
    is_circular_definition: bool = False
    shallow_penalty_applied: float = 0.0


class ParameterScoreBreakdown(BaseModel):
    """Raw and weighted scores across the 4 parameters."""
    accuracy: float = Field(..., ge=0.0, le=1.0)
    depth: float = Field(..., ge=0.0, le=1.0)
    logical_reasoning: float = Field(..., ge=0.0, le=1.0)
    real_world_applicability: float = Field(..., ge=0.0, le=1.0)
    weighted_composite_raw: float = Field(..., ge=0.0, le=1.0)


class NormalizedTurnScore(BaseModel):
    """Score adjusted for difficulty rating and experience tier."""
    raw_score: float = Field(..., ge=0.0, le=1.0)
    difficulty_level: int = Field(..., ge=1, le=5)
    difficulty_weight_multiplier: float = Field(..., ge=0.5, le=2.0)
    normalized_score: float = Field(..., ge=0.0, le=100.0)
    irt_proficiency_theta: float = Field(..., description="Estimated candidate latent ability theta")


class ExplainableScoringOutput(BaseModel):
    """Human-in-the-loop explainable evaluation dossier for a turn."""
    turn_index: int
    question_id: str
    question_category: str
    difficulty_level: int
    parameter_scores: ParameterScoreBreakdown
    shallow_diagnostics: ShallowAnswerDiagnostics
    normalized_scoring: NormalizedTurnScore
    justification_summary: str
    positive_technical_evidence: List[str]
    identified_gaps: List[str]
    counterfactual_guidance: str


# ==============================================================================
# 4. SKILL-WISE SCORING BREAKDOWN & FINAL REPORT FORMAT
# ==============================================================================

class SkillDomainScore(BaseModel):
    """Aggregated assessment for a specific skill domain."""
    domain_id: str
    domain_name: str
    turns_evaluated: int
    raw_average_score: float = Field(..., ge=0.0, le=100.0)
    difficulty_weighted_score: float = Field(..., ge=0.0, le=100.0)
    proficiency_level: SkillProficiencyLevel
    parameter_averages: Dict[str, float]
    demonstrated_subskills: List[str]
    deficient_subskills: List[str]


class TechnicalEvaluationReportFormat(BaseModel):
    """
    Standardized, audit-grade technical evaluation report format (Deliverable 3).
    Provides structured data exportable to JSON, Markdown, and PDF.
    """
    report_id: str
    candidate_id: str
    target_role: str
    experience_tier: str
    session_id: str
    timestamp: float = Field(default_factory=time.time)

    # High-level metrics
    final_technical_score: float = Field(..., ge=0.0, le=100.0)
    overall_irt_proficiency: float
    hiring_recommendation: str
    overall_depth_classification: AnswerDepthClassification

    # Parameter Radar
    parameter_aggregate_scores: Dict[str, float]

    # Skill-Wise Breakdown (Deliverable 2)
    skill_domain_breakdown: List[SkillDomainScore]

    # Detailed Explainable Turns
    turn_evaluations: List[ExplainableScoringOutput]

    # Executive Commentary
    key_strengths: List[str]
    critical_growth_areas: List[str]
    counterfactual_improvement_plan: List[str]
    regulatory_compliance_attestation: Dict[str, Any]
    scoring_integrity_hash: str = Field(default="", description="Cryptographic SHA-256 seal of evaluation")
