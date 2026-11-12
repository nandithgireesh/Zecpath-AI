"""
Day 37: HR Interview Scoring Models & Schemas
==============================================
Pydantic data models and enumerations defining the four core scoring parameters:
- Answer Relevance
- Communication Score
- Confidence Score
- Consistency
along with weight profiles, explainability breakdowns, length normalization parameters,
and the candidate HR score report schema.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HiringRecommendation(str, Enum):
    """Calibrated recruiter decision recommendations."""
    STRONG_HIRE = "STRONG_HIRE"          # >= 88.0
    HIRE = "HIRE"                        # 76.0 - 87.9
    LEAN_HIRE = "LEAN_HIRE"              # 65.0 - 75.9
    LEAN_NO_HIRE = "LEAN_NO_HIRE"        # 50.0 - 64.9
    NO_HIRE = "NO_HIRE"                  # < 50.0


class ScoringParameter(str, Enum):
    """The four core parameters mandated by Day 37 curriculum."""
    ANSWER_RELEVANCE = "answer_relevance"
    COMMUNICATION = "communication_score"
    CONFIDENCE = "confidence_score"
    CONSISTENCY = "consistency"


class RoleTrackPreset(str, Enum):
    """Pre-configured enterprise role track profiles."""
    TECHNICAL_ROLES = "technical_roles"
    LEADERSHIP_ROLES = "leadership_roles"
    CLIENT_FACING_ROLES = "client_facing_roles"
    CAMPUS_FRESHER_ROLES = "campus_fresher_roles"
    STANDARD_BALANCED = "standard_balanced"


class WeightProfile(BaseModel):
    """Configurable weight profile for the 4 scoring parameters."""
    profile_name: str = Field(..., description="Descriptive profile or role title")
    answer_relevance: float = Field(0.30, ge=0.05, le=0.60, description="Weight for answer relevance")
    communication: float = Field(0.25, ge=0.05, le=0.60, description="Weight for communication skills")
    confidence: float = Field(0.25, ge=0.05, le=0.60, description="Weight for behavioral confidence")
    consistency: float = Field(0.20, ge=0.05, le=0.60, description="Weight for factual & narrative consistency")
    description: Optional[str] = Field(None, description="Recruiting context or rationale for this weight matrix")

    def validate_weights(self) -> bool:
        """Validates that weights sum to 1.0 within floating point precision."""
        total = self.answer_relevance + self.communication + self.confidence + self.consistency
        return abs(total - 1.0) < 1e-4

    def as_dict(self) -> Dict[str, float]:
        """Returns weights mapped by parameter key."""
        return {
            ScoringParameter.ANSWER_RELEVANCE.value: self.answer_relevance,
            ScoringParameter.COMMUNICATION.value: self.communication,
            ScoringParameter.CONFIDENCE.value: self.confidence,
            ScoringParameter.CONSISTENCY.value: self.consistency,
        }


class TurnRelevanceEvaluation(BaseModel):
    """Evaluation of answer relevance for a single turn."""
    turn_index: int = Field(..., description="Zero-indexed turn number")
    raw_relevance_score: float = Field(..., ge=0.0, le=100.0, description="Unnormalized relevance score")
    intent_match_score: float = Field(..., ge=0.0, le=100.0, description="Semantic alignment with question intent")
    keyword_coverage_score: float = Field(..., ge=0.0, le=100.0, description="Domain and context term coverage")
    substantive_depth_score: float = Field(..., ge=0.0, le=100.0, description="Concrete technical/behavioral detail vs fluff")
    detected_intent_themes: List[str] = Field(default_factory=list, description="Themes matched to question requirement")
    missing_aspects: List[str] = Field(default_factory=list, description="Aspects asked but unanswered")


class LengthNormalizationMetadata(BaseModel):
    """Telemetry capturing length normalization across different interview lengths."""
    total_turns_evaluated: int = Field(..., description="Number of candidate responses evaluated")
    expected_standard_turns: int = Field(5, description="Benchmark turn count for standard interview")
    raw_average_score: float = Field(..., ge=0.0, le=100.0, description="Simple arithmetic mean of turn scores")
    normalized_score: float = Field(..., ge=0.0, le=100.0, description="Length-normalized composite score")
    prior_mean: float = Field(70.0, description="Bayesian smoothing prior mean")
    prior_weight_m: float = Field(2.0, description="Bayesian smoothing weight factor")
    recency_weighted_average: float = Field(..., ge=0.0, le=100.0, description="Recency/turn-decay weighted mean")
    session_completeness_factor: float = Field(1.0, ge=0.5, le=1.05, description="Interview phase completeness scaling")
    normalization_adjustment: float = Field(0.0, description="Delta applied to raw average (normalized - raw)")


class ParameterContribution(BaseModel):
    """Detailed explainable breakdown for a single scoring parameter."""
    parameter: ScoringParameter = Field(..., description="Scoring parameter enum")
    display_name: str = Field(..., description="Human-readable parameter title")
    raw_score: float = Field(..., ge=0.0, le=100.0, description="Raw parameter score")
    normalized_score: float = Field(..., ge=0.0, le=100.0, description="Length-normalized parameter score")
    weight: float = Field(..., ge=0.0, le=1.0, description="Assigned weight in profile")
    weighted_contribution: float = Field(..., ge=0.0, le=100.0, description="Points contributed to composite score (norm * weight)")
    percentage_of_total: float = Field(..., ge=0.0, le=100.0, description="Relative percentage contribution to final score")
    diagnostic_summary: str = Field(..., description="Brief recruiter explanation of the score")


class CandidateHRScoreReport(BaseModel):
    """Master candidate HR score report format mandated by Deliverable 3."""
    # 1. Candidate Metadata
    candidate_id: str = Field(..., description="Unique candidate identifier")
    candidate_name: str = Field(..., description="Full candidate name")
    job_role: str = Field(..., description="Target role title")
    experience_years: float = Field(..., description="Years of professional experience")
    session_id: str = Field(..., description="Interview session ID")
    evaluation_date: str = Field(..., description="Timestamp of evaluation generation")
    weight_profile_used: str = Field(..., description="Weight configuration profile applied")

    # 2. Executive Verdict
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Final weighted composite score (0-100)")
    recommendation: HiringRecommendation = Field(..., description="Hiring decision tier")
    executive_summary: str = Field(..., description="Recruiter executive summary paragraph")

    # 3. Parameter Breakdown (The 4 core parameters)
    parameter_breakdown: Dict[str, ParameterContribution] = Field(..., description="Detailed breakdown for each parameter")

    # 4. Length Normalization Telemetry
    length_normalization: LengthNormalizationMetadata = Field(..., description="Interview length normalization telemetry")

    # 5. Granular Sub-Dimension Ratings
    communication_subdimensions: Dict[str, float] = Field(..., description="Fluency, Grammar, Vocab, Clarity, Fillers, Structure")
    behavioral_subdimensions: Dict[str, float] = Field(..., description="Hesitation, Sentiment Composure, Narrative Consistency, Stress Index")

    # 6. Turn-by-Turn Trajectory
    turn_score_trajectory: List[Dict[str, Any]] = Field(default_factory=list, description="Scores per turn across conversation")

    # 7. Actionable Recruiter Feedback
    key_strengths: List[str] = Field(default_factory=list, description="Top positive candidate attributes")
    risk_flags: List[str] = Field(default_factory=list, description="Identified inconsistencies, stress, or relevance gaps")
    recommended_next_steps: List[str] = Field(default_factory=list, description="Actionable next round suggestions")
