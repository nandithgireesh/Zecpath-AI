"""
Day 40: HR Interview Simulation & Accuracy Evaluation Models
============================================================
Pydantic data models and enumerations defining:
- Candidate simulation archetypes (Confident, Hesitant, Inexperienced, Overqualified, Inconsistent)
- Human evaluation ground truth benchmarks and expert panel rubrics
- Accuracy comparison metrics (MAE, RMSE, Pearson r, Decision Concordance)
- Scoring inconsistency and edge-case boundary telemetry
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from .hr_scoring_models import HiringRecommendation, RoleTrackPreset


class CandidateArchetype(str, Enum):
    """Core candidate simulation profiles mandated by Day 40 curriculum."""
    CONFIDENT = "CONFIDENT"              # High technical depth, articulate, resilient, STAR-aligned
    HESITANT = "HESITANT"                # Competent knowledge, but frequent pauses, fillers, hedging
    INEXPERIENCED = "INEXPERIENCED"      # Low tenure, shallow trade-offs, vague explanations, junior mindset
    OVERQUALIFIED = "OVERQUALIFIED"      # Principal/Staff level depth, excessive detail for target role, low stress
    INCONSISTENT = "INCONSISTENT"        # Contradictory claims, blame deflection, cognitive fallacies


class HumanExpertPanelScore(BaseModel):
    """Calibrated ground-truth evaluation from senior human hiring panel."""
    evaluator_role: str = Field(..., description="Role of expert (e.g. Senior HR Director, Bar Raiser)")
    behavioral_score: float = Field(..., ge=0.0, le=100.0, description="STAR behavioral execution score")
    communication_score: float = Field(..., ge=0.0, le=100.0, description="Verbal articulation & hygiene score")
    composure_score: float = Field(..., ge=0.0, le=100.0, description="Composure & stress handling score")
    aptitude_score: float = Field(..., ge=0.0, le=100.0, description="Logical reasoning & problem-solving score")
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Consensus weighted human composite score")
    recommendation: HiringRecommendation = Field(..., description="Consensus human hiring recommendation")
    notes: str = Field(..., description="Human expert observations and qualitative remarks")


class SimulatedCandidateProfile(BaseModel):
    """Complete specification of a simulated candidate."""
    candidate_id: str = Field(..., description="Unique simulated candidate ID")
    name: str = Field(..., description="Simulated candidate name")
    target_role: str = Field(..., description="Target role applied for")
    experience_years: float = Field(..., description="Claimed years of professional experience")
    archetype: CandidateArchetype = Field(..., description="Simulation archetype category")
    role_track: RoleTrackPreset = Field(default=RoleTrackPreset.TECHNICAL_ROLES)
    expected_recommendation: HiringRecommendation = Field(...)
    human_ground_truth: HumanExpertPanelScore = Field(...)


class SimulationTurnData(BaseModel):
    """Telemetry capturing an individual turn during simulation."""
    turn_index: int = Field(...)
    phase: str = Field(...)
    question_asked: str = Field(...)
    candidate_response: str = Field(...)
    hesitation_seconds: float = Field(..., ge=0.0)
    filler_percentage: float = Field(..., ge=0.0)
    stress_index: float = Field(..., ge=0.0, le=100.0)
    relevance_score: float = Field(..., ge=0.0, le=100.0)
    dynamic_followup_triggered: bool = Field(default=False)
    followup_reason: Optional[str] = None


class SessionSimulationResult(BaseModel):
    """End-to-end simulation output for a single candidate session."""
    session_id: str = Field(...)
    candidate: SimulatedCandidateProfile = Field(...)
    turns_executed: List[SimulationTurnData] = Field(default_factory=list)
    ai_composite_score: float = Field(..., ge=0.0, le=100.0)
    ai_recommendation: HiringRecommendation = Field(...)
    human_composite_score: float = Field(..., ge=0.0, le=100.0)
    human_recommendation: HiringRecommendation = Field(...)
    score_variance: float = Field(..., description="Delta: AI Composite - Human Composite")
    decision_match: bool = Field(..., description="Whether AI recommendation exactly matched human panel")
    tier_distance: int = Field(default=0, description="Step distance between decision tiers (0 = exact, 1 = adjacent)")
    inconsistencies_detected: int = Field(default=0)
    cultural_fit_average: float = Field(default=0.0)
    summary_markdown_path: Optional[str] = None
    summary_json_path: Optional[str] = None


class DiscrepancyAnalysis(BaseModel):
    """Detailed diagnosis of scoring divergence between AI and human panel."""
    candidate_id: str = Field(...)
    archetype: CandidateArchetype = Field(...)
    ai_score: float = Field(...)
    human_score: float = Field(...)
    delta: float = Field(...)
    discrepancy_type: str = Field(..., description="Classification (e.g. HESITATION_BIAS, OVERQUALIFICATION_DIVERGENCE)")
    root_cause: str = Field(..., description="Underlying algorithmic mechanism driving the delta")
    remediation_recommendation: str = Field(..., description="Recommended tuning or heuristic adjustment")


class AccuracyBenchmarkReport(BaseModel):
    """Statistical accuracy evaluation across the entire simulation cohort."""
    total_sessions_simulated: int = Field(...)
    archetypes_evaluated: List[CandidateArchetype] = Field(...)
    mean_absolute_error: float = Field(..., description="MAE across composite scores")
    root_mean_squared_error: float = Field(..., description="RMSE across composite scores")
    pearson_correlation: float = Field(..., ge=-1.0, le=1.0, description="Pearson r correlation coefficient")
    spearman_rank_correlation: float = Field(..., ge=-1.0, le=1.0, description="Spearman rho rank correlation")
    exact_decision_concordance_pct: float = Field(..., ge=0.0, le=100.0, description="% exact recommendation match")
    adjacent_decision_concordance_pct: float = Field(..., ge=0.0, le=100.0, description="% within 1 tier (e.g. Hire vs Strong Hire)")
    precision_macro: float = Field(..., ge=0.0, le=1.0)
    recall_macro: float = Field(..., ge=0.0, le=1.0)
    f1_macro: float = Field(..., ge=0.0, le=1.0)
    identified_discrepancies: List[DiscrepancyAnalysis] = Field(default_factory=list)
    generated_at: str = Field(...)
