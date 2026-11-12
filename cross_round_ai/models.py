"""
Zecpath-AI: Day 51 - Cross-Round Aggregation Engine Models
==========================================================
Data models, enumerations, and schemas defining the complete 5-stage unified hiring intelligence:
1. Five Canonical Assessment Stages: ATS, Screening, HR Interview, Technical Interview, Machine Test
2. Role-Based Weight Configurations & Gating Thresholds
3. Candidate Experience Profiles & Profile Normalization Telemetry
4. Transparent Scoring Contributions, Risk Discounts & Counterfactuals
5. Unified Candidate Score Object (Deliverable 3)

Curriculum Reference: Day 51 - Cross-Round Aggregation Engine
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
import hashlib


# ==============================================================================
# 1. CORE ENUMERATIONS
# ==============================================================================

class AssessmentStage(str, Enum):
    """The five canonical evaluation stages of the end-to-end Zecpath-AI pipeline."""
    ATS_RESUME = "ATS_RESUME"                        # Stage 1 (Days 1-20): Parsing, relevance, skills match
    CONVERSATIONAL_SCREENING = "SCREENING"           # Stage 2 (Days 21-32): Voice phone screening, eligibility
    HR_BEHAVIORAL_INTERVIEW = "HR_INTERVIEW"         # Stage 3 (Days 33-45): Behavioral STAR, culture, composure
    TECHNICAL_INTERVIEW = "TECHNICAL_INTERVIEW"      # Stage 4 (Days 46-47): Bloom's taxonomy, DDA, skill depth
    MACHINE_TEST = "MACHINE_TEST"                    # Stage 5 (Day 50): Practical coding, debugging, sandbox ETL


class RoleWeightProfile(str, Enum):
    """Industry role archetypes determining cross-stage weight distribution."""
    SOFTWARE_ENGINEERING = "SOFTWARE_ENGINEERING"          # High weight on Tech & Machine Test
    DISTRIBUTED_SYSTEMS_LEAD = "DISTRIBUTED_SYSTEMS_LEAD"  # Extreme weight on Architecture & System Design
    ENGINEERING_MANAGEMENT = "ENGINEERING_MANAGEMENT"      # Balanced Tech & High HR/Leadership
    DATA_PLATFORM_ENGINEERING = "DATA_PLATFORM_ENG"        # High Machine Test / ETL & Problem Solving
    SOLUTIONS_ARCHITECTURE = "SOLUTIONS_ARCHITECTURE"      # High Screening, HR, and Conceptual Tech
    CUSTOM_ROLE = "CUSTOM_ROLE"


class CandidateProfileTier(str, Enum):
    """Experience tiers for profile-aware normalization."""
    ENTRY_LEVEL_0_2 = "ENTRY_LEVEL_0_2"
    MID_LEVEL_3_5 = "MID_LEVEL_3_5"
    SENIOR_LEAD_5_PLUS = "SENIOR_LEAD_5_PLUS"
    PRINCIPAL_ARCHITECT = "PRINCIPAL_ARCHITECT"


class HiringDecision(str, Enum):
    """Calibrated unified hiring decision verdict."""
    STRONG_HIRE = "STRONG_HIRE"          # >= 85.0 Fit, zero gate failures
    HIRE = "HIRE"                        # 72.0 - 84.9 Fit
    LEAN_HIRE = "LEAN_HIRE"              # 60.0 - 71.9 Fit
    LEAN_NO_HIRE = "LEAN_NO_HIRE"        # 45.0 - 59.9 Fit
    NO_HIRE = "NO_HIRE"                  # < 45.0 Fit or critical gate breach


class ReadinessTier(str, Enum):
    """Organizational deployment readiness."""
    FAST_TRACK_OFFER = "FAST_TRACK_OFFER"
    PRODUCTION_DEPLOYABLE = "PRODUCTION_DEPLOYABLE"
    DEVELOPING_WITH_ONBOARDING = "DEVELOPING_WITH_ONBOARDING"
    BELOW_BAR_UPSKILL = "BELOW_BAR_UPSKILL"
    DISQUALIFIED_HIGH_RISK = "DISQUALIFIED_HIGH_RISK"


# ==============================================================================
# 2. STAGE TELEMETRY & INPUT SCHEMAS
# ==============================================================================

class StageScoreInput(BaseModel):
    """Standardized score telemetry ingested from one of the 5 assessment stages."""
    stage: AssessmentStage
    stage_name: str
    raw_score: float = Field(..., ge=0.0, le=100.0)
    normalized_score: float = Field(..., ge=0.0, le=100.0)
    confidence_weight: float = Field(default=1.0, ge=0.1, le=1.0)
    sub_metrics: Dict[str, float] = Field(default_factory=dict)
    key_strengths: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    completion_timestamp: Optional[str] = None


class StageWeightSpecification(BaseModel):
    """Configured weight and hard gating minimum for an individual stage."""
    weight: float = Field(..., ge=0.0, le=1.0)
    min_cutoff_score: float = Field(default=40.0, ge=0.0, le=100.0, description="Hard disqualification floor")
    is_critical_gate: bool = True


class CrossStageWeightConfig(BaseModel):
    """Complete weight configuration across all 5 evaluation stages."""
    profile_name: str
    role_profile: RoleWeightProfile
    weights: Dict[AssessmentStage, StageWeightSpecification]
    target_experience_tier: CandidateProfileTier = CandidateProfileTier.MID_LEVEL_3_5
    notes: str = ""

    def validate_weights_sum(self) -> bool:
        total = sum(s.weight for s in self.weights.values())
        return abs(total - 1.0) < 1e-4


# ==============================================================================
# 3. TRANSPARENCY & EXPLAINABILITY SCHEMAS
# ==============================================================================

class StageScoreContribution(BaseModel):
    """Detailed explainable breakdown of a single stage's contribution to final fit."""
    stage: AssessmentStage
    stage_name: str
    raw_score: float
    normalized_score: float
    weight: float
    points_contributed: float
    percentage_of_final: float
    passed_gate: bool
    cutoff_threshold: float
    key_strengths: List[str]
    risk_observations: List[str]


class RadarDimensionScore(BaseModel):
    """Holistic synthesized competency radar for candidate comparison."""
    dimension_name: str  # e.g., "Technical Mastery", "Communication & Culture", "Problem Solving"
    score: float = Field(..., ge=0.0, le=100.0)
    percentile_benchmark: float = Field(..., ge=0.0, le=100.0)
    summary: str


class RiskDiscountTelemetry(BaseModel):
    """Transparent risk discount deductions applied to hiring fit score."""
    cross_round_inconsistency_penalty: float = 0.0
    integrity_malpractice_penalty: float = 0.0
    gate_failure_penalty: float = 0.0
    total_risk_discount: float = 0.0
    risk_explanations: List[str] = Field(default_factory=list)


# ==============================================================================
# 4. UNIFIED CANDIDATE SCORE OBJECT (DELIVERABLE 3)
# ==============================================================================

class UnifiedCandidateScoreObject(BaseModel):
    """
    Master unified hiring intelligence dossier synthesizing all 5 assessment rounds
    into an auditable, transparent candidate scorecard.
    """
    candidate_id: str
    candidate_name: str
    applied_role: str
    experience_tier: CandidateProfileTier
    weight_profile_used: RoleWeightProfile
    evaluation_timestamp: str

    # Core Synthesized Scores
    base_aggregate_score: float = Field(..., ge=0.0, le=100.0)
    risk_discounts: RiskDiscountTelemetry
    hiring_fit_score: float = Field(..., ge=0.0, le=100.0, description="Final Calibrated Hiring Fit (%)")

    # Hiring Verdicts
    decision_verdict: HiringDecision
    readiness_tier: ReadinessTier
    calibrated_leveling: str  # e.g., "Senior Software Engineer (L5)"

    # Transparency & Explainability Details
    stage_contributions: Dict[AssessmentStage, StageScoreContribution]
    radar_competencies: List[RadarDimensionScore]
    executive_summary: str
    hiring_manager_action: str
    counterfactual_guidance: str

    # Integrity & Compliance Verification
    all_gates_passed: bool
    audit_hash_sha256: str
