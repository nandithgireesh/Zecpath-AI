"""
Day 52: Final Recommendation AI - Core Domain Models & Schemas (Deliverable 3)
=============================================================================
Defines standard enums, telemetry structures, risk factor payloads, and the
enterprise Candidate Decision Output format certified via SHA-256.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import hashlib
import json


# ==============================================================================
# 1. CORE ENUMERATIONS
# ==============================================================================

class FinalDecisionCategory(str, Enum):
    """The three canonical hiring decision outcomes mandated by Day 52 specification."""
    SELECTED = "SELECTED"          # Direct offer / clear hire
    HOLD_REVIEW = "HOLD_REVIEW"    # Conditional hold, manager review, or bar-raiser required
    REJECTED = "REJECTED"          # Formal disqualification / no-hire verdict


class DecisionSubStatus(str, Enum):
    """Granular actionable sub-classification for recruitment workflows."""
    # SELECTED sub-statuses
    OFFER_IMMEDIATE_FAST_TRACK = "OFFER_IMMEDIATE_FAST_TRACK"
    OFFER_STANDARD = "OFFER_STANDARD"
    OFFER_LEVEL_UPGRADE = "OFFER_LEVEL_UPGRADE"
    
    # HOLD_REVIEW sub-statuses
    HOLD_HIRING_MANAGER_DEBRIEF = "HOLD_HIRING_MANAGER_DEBRIEF"
    HOLD_BAR_RAISER_EVALUATION = "HOLD_BAR_RAISER_EVALUATION"
    HOLD_INTEGRITY_AUDIT = "HOLD_INTEGRITY_AUDIT"
    HOLD_BORDERLINE_SKILL_RETEST = "HOLD_BORDERLINE_SKILL_RETEST"
    
    # REJECTED sub-statuses
    REJECT_CRITICAL_GATE_BREACH = "REJECT_CRITICAL_GATE_BREACH"
    REJECT_LOW_OVERALL_FIT = "REJECT_LOW_OVERALL_FIT"
    REJECT_INTEGRITY_MALPRACTICE = "REJECT_INTEGRITY_MALPRACTICE"
    REJECT_COMPETENCY_CONTRADICTION = "REJECT_COMPETENCY_CONTRADICTION"


class OverallRiskLevel(str, Enum):
    """Composite risk categorization synthesizing behavioral and integrity signals."""
    LOW = "LOW"                    # Minor or zero risk factors detected
    MODERATE = "MODERATE"          # Isolated behavioral pauses or small score variance
    HIGH = "HIGH"                  # Notable red flags, contradictions, or high stress
    CRITICAL = "CRITICAL"          # Disqualifying integrity malpractice or gate breach


class ConfidenceBand(str, Enum):
    """Categorized certainty tier for the algorithmic recommendation."""
    VERY_HIGH = "VERY_HIGH"        # Confidence >= 90.0%
    HIGH = "HIGH"                  # Confidence 78.0% - 89.9%
    MODERATE = "MODERATE"          # Confidence 60.0% - 77.9%
    LOW = "LOW"                    # Confidence < 60.0% (ambiguous signals, high variance)


class RuleStatus(str, Enum):
    """Outcome status of an automated decision rule evaluation."""
    PASSED = "PASSED"
    FLAGGED = "FLAGGED"
    FAILED_CRITICAL = "FAILED_CRITICAL"


# ==============================================================================
# 2. RISK FACTOR TELEMETRY
# ==============================================================================

class BehavioralRiskFactor(BaseModel):
    """Individual behavioral anomaly or concern."""
    factor_id: str
    dimension: str                 # e.g., 'STRESS_RESILIENCE', 'COMMUNICATION', 'ETHICS'
    severity: OverallRiskLevel
    description: str
    deduction_points: float = 0.0


class IntegrityRiskFactor(BaseModel):
    """Individual integrity or malpractice concern from Day 49 / Day 50."""
    factor_id: str
    category: str                  # e.g., 'MALPRACTICE', 'PLAGIARISM', 'RESUME_INFLATION'
    severity: OverallRiskLevel
    evidence: str
    deduction_points: float = 0.0


class RiskFactorsTelemetry(BaseModel):
    """Consolidated behavioral and integrity risk analysis."""
    overall_risk_level: OverallRiskLevel = OverallRiskLevel.LOW
    total_risk_penalty_points: float = 0.0
    behavioral_risks: List[BehavioralRiskFactor] = Field(default_factory=list)
    integrity_risks: List[IntegrityRiskFactor] = Field(default_factory=list)
    has_disqualifying_breach: bool = False
    risk_summary_note: str = ""


# ==============================================================================
# 3. HYBRID RULE EVALUATION TELEMETRY
# ==============================================================================

class EvaluatedRule(BaseModel):
    """Outcome of a single deterministic policy rule."""
    rule_id: str
    rule_name: str
    is_critical_gate: bool
    status: RuleStatus
    threshold_applied: str
    observed_value: str
    reasoning: str


# ==============================================================================
# 4. DECISION CONFIDENCE TELEMETRY
# ==============================================================================

class DecisionConfidenceTelemetry(BaseModel):
    """Quantified mathematical certainty of the AI recommendation."""
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Overall decision confidence %")
    confidence_band: ConfidenceBand
    boundary_distance_factor: float = Field(..., description="Margin distance from nearest decision threshold")
    signal_consistency_factor: float = Field(..., description="Statistical variance stability across rounds")
    data_completeness_factor: float = Field(..., description="Completeness of assessment stage data ingested")
    confidence_rationale: str = ""


# ==============================================================================
# 5. EXPLAINABILITY & COUNTERFACTUAL TELEMETRY
# ==============================================================================

class ExplainableDriver(BaseModel):
    """A primary factor explaining why the decision was reached."""
    driver_type: str               # 'POSITIVE_STRENGTH' or 'RISK_BLOCKER'
    dimension_name: str
    impact_points: float
    explanation: str


class CounterfactualGuidance(BaseModel):
    """Actionable prescriptive condition detailing how the decision would change."""
    target_category: FinalDecisionCategory
    required_modifications: List[str]
    feasibility_notes: str


# ==============================================================================
# 6. UNIFIED CANDIDATE DECISION OUTPUT (DELIVERABLE 3)
# ==============================================================================

class CandidateDecisionOutput(BaseModel):
    """
    Enterprise-grade, audit-ready Candidate Decision Output Schema (Deliverable 3).
    Encapsulates final category, substatus, hybrid rule trace, confidence score,
    risk factors, explainable reasoning, and tamper-evident SHA-256 seal.
    """
    # Identification & Pipeline Metadata
    candidate_id: str
    candidate_name: str
    target_role: str
    role_weight_profile: str
    experience_tier: str
    evaluation_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    engine_version: str = "1.0.0-PROD"

    # Core Decision Outcomes
    decision_category: FinalDecisionCategory
    decision_substatus: DecisionSubStatus
    hiring_fit_score: float = Field(..., ge=0.0, le=100.0, description="Calibrated fit percentage from Day 51")
    decision_confidence: DecisionConfidenceTelemetry

    # Multi-Stage Raw & Contribution Overview
    stage_scores_summary: Dict[str, float] = Field(default_factory=dict)

    # Hybrid Rules & Gating Trace
    hybrid_rules_evaluated: List[EvaluatedRule] = Field(default_factory=list)
    all_critical_rules_passed: bool = True

    # Risk Factors (Behavioral & Integrity)
    risk_factors: RiskFactorsTelemetry

    # Explainability & Counterfactual
    primary_positive_drivers: List[ExplainableDriver] = Field(default_factory=list)
    critical_risk_blockers: List[ExplainableDriver] = Field(default_factory=list)
    counterfactual_guidance: Optional[CounterfactualGuidance] = None
    executive_decision_rationale: str

    # Verification & Telemetry
    evaluation_latency_ms: float = 0.0
    audit_hash: str = ""

    def compute_sha256_audit_seal(self) -> str:
        """Computes deterministic SHA-256 signature sealing the candidate decision."""
        seal_payload = {
            "candidate_id": self.candidate_id,
            "target_role": self.target_role,
            "decision_category": self.decision_category.value,
            "decision_substatus": self.decision_substatus.value,
            "hiring_fit_score": round(self.hiring_fit_score, 2),
            "confidence_score": round(self.decision_confidence.confidence_score, 2),
            "risk_level": self.risk_factors.overall_risk_level.value,
            "all_rules_passed": self.all_critical_rules_passed,
        }
        raw_json = json.dumps(seal_payload, sort_keys=True)
        return hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

    def finalize_and_seal(self) -> None:
        """Computes and locks the audit hash seal."""
        self.audit_hash = self.compute_sha256_audit_seal()
