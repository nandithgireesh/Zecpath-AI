"""
Day 41: Unified Candidate Score Object & Data Models (Deliverable 3)
===================================================================
Pydantic data models, enumerations, and schemas defining:
1. Multi-round scoring inputs (ATS Resume, Pre-Screening, HR Interview)
2. Cross-round role-based weight profiles and gating thresholds
3. Multi-dimensional hiring fit indicators and risk discount metrics
4. Unified Candidate Score Object representing complete end-to-end hiring intelligence
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RoundType(str, Enum):
    """The three canonical evaluation rounds of Zecpath-AI."""
    ATS_RESUME = "ATS_RESUME"                                  # Round 1: Days 1-20
    CONVERSATIONAL_SCREENING = "CONVERSATIONAL_SCREENING"      # Round 2: Days 21-32
    HR_INTERVIEW = "HR_INTERVIEW"                              # Round 3: Days 33-40


class RoleFamily(str, Enum):
    """Role archetypes dictating cross-round weight distributions."""
    TECHNICAL_ENGINEERING = "TECHNICAL_ENGINEERING"
    LEADERSHIP_MANAGEMENT = "LEADERSHIP_MANAGEMENT"
    SALES_CUSTOMER_FACING = "SALES_CUSTOMER_FACING"
    EARLY_CAREER_FRESHER = "EARLY_CAREER_FRESHER"
    OPERATIONS_SUPPORT = "OPERATIONS_SUPPORT"
    CUSTOM_ENTERPRISE = "CUSTOM_ENTERPRISE"


class HiringDecisionTier(str, Enum):
    """Calibrated enterprise hiring recommendations."""
    STRONG_HIRE = "STRONG_HIRE"          # >= 85.0 fit, zero gate failures
    HIRE = "HIRE"                        # 72.0 - 84.9 fit
    LEAN_HIRE = "LEAN_HIRE"              # 60.0 - 71.9 fit
    LEAN_NO_HIRE = "LEAN_NO_HIRE"        # 45.0 - 59.9 fit
    NO_HIRE = "NO_HIRE"                  # < 45.0 fit or critical gate failure


class ReadinessLevel(str, Enum):
    """Candidate organizational readiness classification."""
    IMMEDIATE_FAST_TRACK = "IMMEDIATE_FAST_TRACK"
    PRODUCTION_READY = "PRODUCTION_READY"
    DEVELOPING_WITH_MENTORSHIP = "DEVELOPING_WITH_MENTORSHIP"
    SUB_THRESHOLD_UPSKILL = "SUB_THRESHOLD_UPSKILL"
    OPERATIONAL_RISK_REJECT = "OPERATIONAL_RISK_REJECT"


class RoundScoreInput(BaseModel):
    """Standardized score telemetry ingested from an individual evaluation round."""
    round_type: RoundType = Field(..., description="Evaluation round category")
    round_name: str = Field(..., description="Human-readable round name")
    raw_score: float = Field(..., ge=0.0, le=100.0, description="Raw round score (0-100)")
    normalized_score: float = Field(..., ge=0.0, le=100.0, description="Calibrated score (0-100)")
    confidence_weight: float = Field(default=1.0, ge=0.1, le=1.0, description="Signal confidence factor")
    dimension_breakdown: Dict[str, float] = Field(default_factory=dict, description="Sub-dimensional scores")
    strengths: List[str] = Field(default_factory=list, description="Key round strengths")
    flags_or_penalties: List[str] = Field(default_factory=list, description="Risk flags or deductions")
    source_session_or_doc_id: Optional[str] = Field(default=None, description="Artifact or session reference ID")


class CrossRoundWeightProfile(BaseModel):
    """Role-tailored cross-round weighting distribution and hard safety gates."""
    role_family: RoleFamily = Field(..., description="Target role archetype")
    display_name: str = Field(..., description="Human-readable profile title")
    ats_weight: float = Field(..., ge=0.0, le=1.0, description="Weight for Round 1 (ATS)")
    screening_weight: float = Field(..., ge=0.0, le=1.0, description="Weight for Round 2 (Screening)")
    hr_interview_weight: float = Field(..., ge=0.0, le=1.0, description="Weight for Round 3 (HR Interview)")
    minimum_thresholds: Dict[RoundType, float] = Field(default_factory=dict, description="Hard gate minimum scores")
    rationale: str = Field(..., description="Organizational justification for weight profile")


class RoundContribution(BaseModel):
    """Quantified contribution of a single round to the composite score."""
    round_type: RoundType
    display_name: str
    raw_score: float = Field(..., ge=0.0, le=100.0)
    effective_weight: float = Field(..., ge=0.0, le=1.0)
    weighted_points: float = Field(..., ge=0.0, le=100.0)
    passed_gate: bool = Field(default=True)
    gate_threshold: float = Field(default=0.0)
    status_note: str = ""


class HiringFitBreakdown(BaseModel):
    """Multi-dimensional breakdown of candidate hiring fit and readiness."""
    technical_competence_fit: float = Field(..., ge=0.0, le=100.0, description="Skills, experience & technical logic fit")
    communication_clarity_fit: float = Field(..., ge=0.0, le=100.0, description="Verbal hygiene, articulation & fluency fit")
    behavioral_culture_fit: float = Field(..., ge=0.0, le=100.0, description="STAR ownership, teamwork & ethics fit")
    adaptability_trajectory_fit: float = Field(..., ge=0.0, le=100.0, description="Learning agility, growth & composure fit")
    risk_and_integrity_discount: float = Field(default=0.0, ge=0.0, description="Penalties deducted for integrity/fallacies")
    net_hiring_fit_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall calibrated hiring fit %")
    calibrated_percentile: float = Field(..., ge=0.0, le=99.9, description="Estimated cohort percentile rank")
    fit_summary: str = Field(..., description="Qualitative hiring fit summary")


class UnifiedCandidateScoreObject(BaseModel):
    """
    Deliverable 3: Master unified hiring intelligence score object integrating
    ATS, Screening, and HR Interview rounds into a single auditable artifact.
    """
    candidate_id: str = Field(..., description="Unique candidate identifier")
    candidate_name: str = Field(..., description="Candidate full name")
    target_role: str = Field(..., description="Target job role applied for")
    role_family: RoleFamily = Field(..., description="Assigned role archetype")
    evaluation_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Input round telemetry
    round_inputs: Dict[RoundType, RoundScoreInput] = Field(..., description="Ingested round scores")
    
    # Weight profile & mathematical breakdown
    weight_profile_used: CrossRoundWeightProfile = Field(..., description="Cross-round weight configuration")
    round_contributions: Dict[RoundType, RoundContribution] = Field(..., description="Weighted points breakdown")
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Multi-round weighted composite score")
    
    # Hiring fit calculation
    hiring_fit: HiringFitBreakdown = Field(..., description="Multi-dimensional hiring fit analytics")
    
    # Decision synthesis
    final_decision: HiringDecisionTier = Field(..., description="Consensus hiring decision")
    readiness_level: ReadinessLevel = Field(..., description="Organizational deployment readiness")
    calibrated_role_tier: str = Field(..., description="Specific recommended title or leveling tier")
    executive_verdict: str = Field(..., description="Recruiter executive summary paragraph")
    
    # Qualitative insights & audit
    key_strengths: List[str] = Field(default_factory=list, description="Top positive attributes across rounds")
    developmental_areas: List[str] = Field(default_factory=list, description="Targeted improvement areas")
    safety_gate_passed: bool = Field(default=True, description="Whether all mandatory round gates were satisfied")
    gate_failure_reasons: List[str] = Field(default_factory=list, description="Reasons for any gate rejections")
    audit_metadata: Dict[str, Any] = Field(default_factory=dict, description="Platform version, timing, and hash")
