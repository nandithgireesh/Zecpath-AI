"""
Day 30 - Optimization & Testing Models
=======================================
Pydantic data models for candidate archetypes, human recruiter ground truth,
evaluation metrics, threshold configurations, simulated call results, and
optimization comparison reports.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from screening_ai.report_models import HiringRecommendation
from screening_ai.intent_models import CandidateIntent
from screening_ai.flow_models import ConversationState, ActionType



class CandidateArchetype(str, Enum):
    EXPERT_FLUENT = "EXPERT_FLUENT"
    EXPERT_TERSE = "EXPERT_TERSE"
    NERVOUS_COMPETENT = "NERVOUS_COMPETENT"
    BORDERLINE_NEGOTIABLE = "BORDERLINE_NEGOTIABLE"
    NON_NATIVE_ACCENTED = "NON_NATIVE_ACCENTED"
    UNDERQUALIFIED_EVASIVE = "UNDERQUALIFIED_EVASIVE"
    DEFLECTIVE_OFFTOPIC = "DEFLECTIVE_OFFTOPIC"


class HumanRecruiterGroundTruth(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0)
    technical_score: float = Field(..., ge=0.0, le=100.0)
    communication_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: HiringRecommendation
    rationale: str
    false_rejection_risk: str = "LOW"


class ThresholdConfig(BaseModel):
    name: str = "default"
    overall_hire_cutoff: float = Field(default=72.0, ge=50.0, le=90.0)
    strong_hire_cutoff: float = Field(default=85.0, ge=75.0, le=95.0)
    proceed_caution_cutoff: float = Field(default=55.0, ge=40.0, le=70.0)
    technical_hire_cutoff: float = Field(default=68.0, ge=50.0, le=85.0)
    communication_hire_cutoff: float = Field(default=65.0, ge=45.0, le=80.0)
    # Day 30 Optimizations
    enable_tech_compensation: bool = True
    tech_compensation_threshold: float = Field(default=78.0, ge=70.0, le=90.0)
    min_comp_floor_with_tech: float = Field(default=55.0, ge=40.0, le=65.0)
    brevity_protection: bool = True
    brevity_word_threshold: int = 15
    hesitation_penalty_dampener: bool = True
    max_hesitation_penalty: float = 10.0
    enable_second_look_routing: bool = True
    second_look_min_score: float = 65.0


class EvaluationMetrics(BaseModel):
    total_evaluations: int
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_rejection_rate: float
    false_acceptance_rate: float
    cohens_kappa: float
    score_mae: float


class SimulationTurnResult(BaseModel):
    turn_index: int
    question_id: str
    question_text: str
    candidate_utterance: str
    detected_intent: str
    expected_intent: str
    intent_match: bool
    state_before: str
    state_after: str
    emitted_action: str
    latency_ms: int
    turn_score: float


class SimulatedCallResult(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str
    target_role: str
    archetype: CandidateArchetype
    total_turns: int
    call_duration_seconds: float
    turns: List[SimulationTurnResult] = Field(default_factory=list)
    ai_overall_score: float
    ai_technical_score: float
    ai_communication_score: float
    ai_recommendation: HiringRecommendation
    human_recommendation: HiringRecommendation
    recommendation_matches: bool
    is_false_rejection: bool
    is_false_acceptance: bool
    summary_notes: str


class OptimizationComparisonReport(BaseModel):
    report_id: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    baseline_thresholds: ThresholdConfig

    optimized_thresholds: ThresholdConfig
    baseline_metrics: EvaluationMetrics
    optimized_metrics: EvaluationMetrics
    false_rejection_reduction_pct: float
    resolved_candidates: List[str] = Field(default_factory=list)
    benchmark_profiles_evaluated: int
    key_takeaways: List[str] = Field(default_factory=list)
