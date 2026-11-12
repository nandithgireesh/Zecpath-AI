"""
Day 48: Behavioral AI Data Models & Observable Signal Schemas
=============================================================
Pydantic schemas defining observable non-invasive behavioral telemetry:
- Eye movement & gaze stability (gaze vector, fixation, saccades, blink rate)
- Head movement (pitch, yaw, roll velocities, nods, tilts, stability)
- Facial engagement (Action Units, micro-expressions, smile genuineness, responsiveness)
- Attention patterns (screen dwell, off-screen lookaways, continuous attention span)
- Measurable indicators (Focus Level, Distraction Frequency, Nervous Gestures)
- Behavioral Insights (Composed & Attentive, Deliberating, Mild Anxiety, Disengaged)
- Standardized Behavioral Analysis Report Format (Deliverables 1, 2, 3)

Curriculum Reference: Day 48 - Behavioral AI Research & Design
Statutory Compliance: Illinois BIPA (740 ILCS 14/), EU AI Act Article 9/10, NYC Local Law 144
"""

from typing import List, Dict, Optional, Any, Set, Tuple
from enum import Enum
import time
from pydantic import BaseModel, Field


# ==============================================================================
# 1. ENUMERATIONS: OBSERVABLE SIGNALS & BEHAVIORAL STATES
# ==============================================================================

class GazeDirection(str, Enum):
    """Observable gaze vector classifications relative to interview interface."""
    DIRECT_SCREEN_CENTER = "DIRECT_SCREEN_CENTER"
    SLIGHT_OFF_CENTER = "SLIGHT_OFF_CENTER"
    OFF_SCREEN_LEFT = "OFF_SCREEN_LEFT"
    OFF_SCREEN_RIGHT = "OFF_SCREEN_RIGHT"
    LOOKING_UP_THINKING = "LOOKING_UP_THINKING"
    LOOKING_DOWN_NOTES = "LOOKING_DOWN_NOTES"
    RAPID_SACCADIC_SHIFT = "RAPID_SACCADIC_SHIFT"


class HeadPoseMovement(str, Enum):
    """Observable head movement orientation and kinetic dynamics."""
    STABLE_CENTERED = "STABLE_CENTERED"
    AFFIRMATIVE_NOD = "AFFIRMATIVE_NOD"
    RECEPTIVE_TILT = "RECEPTIVE_TILT"
    RESTLESS_TURNING = "RESTLESS_TURNING"
    DOWNWARD_DROOP = "DOWNWARD_DROOP"
    SUDDEN_JERK = "SUDDEN_JERK"


class FacialEngagementState(str, Enum):
    """Observable facial micro-expression responsiveness."""
    HIGHLY_ENGAGED_RESPONSIVE = "HIGHLY_ENGAGED_RESPONSIVE"
    NATURAL_CALM_COMPOSED = "NATURAL_CALM_COMPOSED"
    DUCHENNE_AUTHENTIC_SMILE = "DUCHENNE_AUTHENTIC_SMILE"
    CONCENTRATED_BROW_FURROW = "CONCENTRATED_BROW_FURROW"
    TENSE_LIP_COMPRESSION = "TENSE_LIP_COMPRESSION"
    FLAT_UNRESPONSIVE_AFFECT = "FLAT_UNRESPONSIVE_AFFECT"


class BehavioralInsightCategory(str, Enum):
    """High-level qualitative behavioral insight synthesis."""
    COMPOSED_AND_ATTENTIVE = "COMPOSED_AND_ATTENTIVE"
    COGNITIVELY_DELIBERATING = "COGNITIVELY_DELIBERATING"
    MILD_INTERVIEW_ANXIETY = "MILD_INTERVIEW_ANXIETY"
    MODERATE_DISTRACTION = "MODERATE_DISTRACTION"
    DISENGAGED_OR_READING = "DISENGAGED_OR_READING"
    NEURODIVERGENT_SAFEGUARDED = "NEURODIVERGENT_SAFEGUARDED"


class EthicalScoringClassification(str, Enum):
    """Statutory non-punitive assessment classification."""
    ASSISTIVE_AFFIRMATIVE = "ASSISTIVE_AFFIRMATIVE"
    NEUTRAL_BASELINE = "NEUTRAL_BASELINE"
    NEURODIVERSE_ADJUSTED = "NEURODIVERSE_ADJUSTED"
    ENVIRONMENTAL_MITIGATED = "ENVIRONMENTAL_MITIGATED"
    HIGH_STRESS_SUPPORT_RECOMMENDED = "HIGH_STRESS_SUPPORT_RECOMMENDED"


# ==============================================================================
# 2. RAW OBSERVABLE TELEMETRY (TRANSIENT FRAME SIGNALS)
# ==============================================================================

class EyeMovementTelemetry(BaseModel):
    """Observable ocular kinematics extracted transiently from video frames."""
    fixation_duration_ms: float = Field(..., ge=0.0, description="Mean gaze fixation dwell duration")
    saccade_velocity_deg_per_sec: float = Field(..., ge=0.0, description="Angular saccadic shift velocity")
    blink_rate_per_minute: float = Field(..., ge=0.0, description="Observed blinks per 60 seconds")
    gaze_stability_index: float = Field(..., ge=0.0, le=1.0, description="Normalized stability score [0.0-1.0]")
    dominant_gaze_direction: GazeDirection = GazeDirection.DIRECT_SCREEN_CENTER
    screen_dwell_ratio: float = Field(..., ge=0.0, le=1.0, description="Percentage of time gazing at camera/screen")


class HeadKinematicsTelemetry(BaseModel):
    """Observable head pose velocities, rotations, and nodding gestures."""
    pitch_velocity_deg_sec: float = Field(..., ge=0.0, description="Up/down rotational velocity")
    yaw_velocity_deg_sec: float = Field(..., ge=0.0, description="Left/right turning rotational velocity")
    roll_velocity_deg_sec: float = Field(..., ge=0.0, description="Side tilt rotational velocity")
    head_stability_index: float = Field(..., ge=0.0, le=1.0, description="Kinematic steadiness score [0.0-1.0]")
    affirmative_nods_count: int = Field(default=0, ge=0, description="Number of receptive conversational nods")
    primary_pose_movement: HeadPoseMovement = HeadPoseMovement.STABLE_CENTERED


class FacialEngagementTelemetry(BaseModel):
    """Observable facial micro-expression Action Units (FACS proxy)."""
    expressiveness_score: float = Field(..., ge=0.0, le=1.0, description="Dynamic facial engagement responsiveness")
    smile_authenticity_ratio: float = Field(..., ge=0.0, le=1.0, description="Duchenne smile co-activation (AU6+AU12)")
    brow_furrow_intensity: float = Field(..., ge=0.0, le=1.0, description="AU4 corrugator tension (cognitive focus proxy)")
    lip_compression_index: float = Field(..., ge=0.0, le=1.0, description="AU24 orbicularis oris tension (nervousness proxy)")
    primary_facial_state: FacialEngagementState = FacialEngagementState.NATURAL_CALM_COMPOSED


class AttentionPatternTelemetry(BaseModel):
    """Observable attention continuity and dispersion dynamics."""
    continuous_attention_span_sec: float = Field(..., ge=0.0, description="Longest unbroken on-screen attention dwell")
    off_screen_lookaway_events: int = Field(..., ge=0, description="Count of off-screen diversion occurrences")
    off_screen_total_duration_sec: float = Field(..., ge=0.0, description="Cumulative diversion duration in seconds")
    multi_monitor_dispersion_detected: bool = Field(default=False, description="Pattern indicating reading off secondary screen")


class RawTurnBehavioralSignals(BaseModel):
    """Aggregated transient observable signals captured during a single interview turn."""
    turn_index: int
    turn_duration_sec: float = Field(..., ge=1.0)
    eye_telemetry: EyeMovementTelemetry
    head_telemetry: HeadKinematicsTelemetry
    facial_telemetry: FacialEngagementTelemetry
    attention_telemetry: AttentionPatternTelemetry


# ==============================================================================
# 3. MEASURABLE BEHAVIORAL INDICATORS (MAPPING TARGETS)
# ==============================================================================

class MeasurableBehavioralIndicators(BaseModel):
    """Quantified, non-invasive behavioral indicators mapped from raw signals."""
    focus_level: float = Field(..., ge=0.0, le=100.0, description="Normalized focus & sustained attention [0-100]")
    distraction_frequency: float = Field(..., ge=0.0, description="Off-screen distraction events per minute")
    nervous_gestures_index: float = Field(..., ge=0.0, le=100.0, description="Stress/anxiety micro-gestures [0-100]")
    cognitive_deliberation_ratio: float = Field(..., ge=0.0, le=1.0, description="Healthy problem-solving thinking gaze ratio")
    conversational_presence_score: float = Field(..., ge=0.0, le=100.0, description="Interpersonal engagement & presence")


# ==============================================================================
# 4. SIGNAL-TO-SCORE MAPPING MODELS (DELIVERABLE 2)
# ==============================================================================

class TurnBehavioralScore(BaseModel):
    """Granular behavioral scoring output for a single interview turn."""
    turn_index: int
    indicators: MeasurableBehavioralIndicators
    composite_behavioral_score: float = Field(..., ge=0.0, le=100.0)
    deliberation_credit_awarded: float = Field(..., ge=0.0, le=15.0)
    neurodiversity_offset_applied: float = Field(..., ge=0.0, le=20.0)
    primary_behavioral_insight: BehavioralInsightCategory
    ethical_classification: EthicalScoringClassification
    observable_positive_evidence: List[str]
    observable_concerns_or_gaps: List[str]


# ==============================================================================
# 5. BEHAVIORAL ANALYSIS REPORT FORMAT (DELIVERABLE 3)
# ==============================================================================

class BehavioralAnalysisReportFormat(BaseModel):
    """
    Standardized, audit-grade Behavioral Analysis Report Format (Deliverable 3).
    Provides structured data exportable to JSON, Markdown, and PDF.
    Statutory Compliance: Illinois BIPA (740 ILCS 14/), EU AI Act Article 9/10, NYC Local Law 144.
    """
    report_id: str
    candidate_id: str
    session_id: str
    target_role: str
    timestamp: float = Field(default_factory=time.time)

    # High-level metrics
    overall_behavioral_score: float = Field(..., ge=0.0, le=100.0)
    overall_focus_index: float = Field(..., ge=0.0, le=100.0)
    average_distraction_rate_per_min: float
    overall_nervousness_index: float = Field(..., ge=0.0, le=100.0)
    primary_behavioral_insight: BehavioralInsightCategory
    ethical_classification: EthicalScoringClassification

    # Granular Radar Aggregates
    indicator_averages: Dict[str, float]

    # Turn-by-Turn Dossier
    turn_evaluations: List[TurnBehavioralScore]

    # Executive Commentary
    key_behavioral_strengths: List[str]
    adaptive_recommendations_for_interviewer: List[str]
    statutory_compliance_attestation: Dict[str, Any]
    audit_integrity_hash: str = Field(default="", description="Cryptographic SHA-256 seal of evaluation")
