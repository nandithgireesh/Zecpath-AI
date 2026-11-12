"""
Day 49: Malpractice & Integrity Detection Models
================================================
Data schemas and telemetry models for browser visibility, external acoustic signals,
visual gaze excursions, malpractice detection flags, alerts, and risk reports.

Curriculum Reference: Day 49 - Malpractice & Integrity Detection Design
Deliverables:
- Deliverable 1: Integrity detection framework
- Deliverable 2: Malpractice detection logic
- Deliverable 3: Risk flagging system design
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class MalpracticeSignalType(str, Enum):
    """Observable signals indicating potential unauthorized assistance or cheating."""
    TAB_SWITCH_BURST = "TAB_SWITCH_BURST"
    LOSS_OF_SCREEN_FOCUS = "LOSS_OF_SCREEN_FOCUS"
    EXTERNAL_VOICE_COLLUSION = "EXTERNAL_VOICE_COLLUSION"
    WHISPERED_AUDIO_PROMPT = "WHISPERED_AUDIO_PROMPT"
    REPEATED_OFF_SCREEN_LOOKAWAY = "REPEATED_OFF_SCREEN_LOOKAWAY"
    SUSPICIOUS_CLIPBOARD_PASTE = "SUSPICIOUS_CLIPBOARD_PASTE"
    MULTI_PERSON_ON_CAMERA = "MULTI_PERSON_ON_CAMERA"
    TEMPORAL_PATTERN_PROMPT_ASSIST = "TEMPORAL_PATTERN_PROMPT_ASSIST"
    LATERAL_PERIPHERY_COLLUSION = "LATERAL_PERIPHERY_COLLUSION"


class FlagSeverity(str, Enum):
    """Hierarchical severity levels for detected integrity events."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertTierLevel(str, Enum):
    """Progressive real-time candidate warning tiers."""
    TIER_0_NOMINAL = "TIER_0_NOMINAL"
    TIER_1_ADVISORY = "TIER_1_ADVISORY"
    TIER_2_FORMAL_WARNING = "TIER_2_FORMAL_WARNING"
    TIER_3_AUDIT_ESCALATION = "TIER_3_AUDIT_ESCALATION"


class InterviewRiskTag(str, Enum):
    """Overall candidate interview integrity risk classification."""
    LOW_RISK_VERIFIED = "LOW_RISK_VERIFIED"
    MODERATE_FLAGGED_REVIEW = "MODERATE_FLAGGED_REVIEW"
    HIGH_RISK_TERMINATE_RECOMMENDED = "HIGH_RISK_TERMINATE_RECOMMENDED"


class BrowserActivityTelemetry(BaseModel):
    """Client-side browser visibility and window interaction telemetry."""
    tab_switch_count: int = Field(default=0, ge=0, description="Count of tab switches during the turn window")
    loss_of_focus_count: int = Field(default=0, ge=0, description="Count of window blur events")
    cumulative_unfocused_time_sec: float = Field(default=0.0, ge=0.0, description="Total seconds interview window was in background")
    clipboard_paste_count: int = Field(default=0, ge=0, description="Count of large external clipboard paste operations")
    devtools_open_flag: bool = Field(default=False, description="Whether browser inspection / devtools were opened")
    fullscreen_exit_count: int = Field(default=0, ge=0, description="Count of exits from enforced fullscreen mode")


class AcousticIntegrityTelemetry(BaseModel):
    """Microphone audio diarization and environmental voice analysis."""
    secondary_speaker_detected: bool = Field(default=False, description="Whether a second human voice was recognized")
    secondary_speaker_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Diarization model confidence")
    background_whisper_detected: bool = Field(default=False, description="Whether low-amplitude whispered speech was isolated")
    audio_overlap_duration_sec: float = Field(default=0.0, ge=0.0, description="Duration in seconds of overlapping speech streams")
    ambient_snr_db: float = Field(default=28.0, description="Signal to noise ratio in decibels")


class VisualIntegrityTelemetry(BaseModel):
    """Webcam visual geometry and peripheral assistance detection."""
    repeated_looking_away_count: int = Field(default=0, ge=0, description="Count of off-screen gaze events")
    lateral_yaw_lookaways_count: int = Field(default=0, ge=0, description="Repetitive lateral head turns (>35 deg yaw)")
    continuous_off_screen_duration_sec: float = Field(default=0.0, ge=0.0, description="Max continuous off-screen stare duration")
    multiple_faces_detected: bool = Field(default=False, description="Whether multiple faces appeared in camera frame")
    absence_from_camera_sec: float = Field(default=0.0, ge=0.0, description="Duration candidate was completely absent from frame")


class RawTurnIntegritySignals(BaseModel):
    """Consolidated telemetry for a single interview turn."""
    turn_index: int = Field(ge=1, description="Sequential index of the interview question/turn")
    turn_duration_sec: float = Field(default=30.0, gt=0.0, description="Duration of the evaluation turn in seconds")
    question_timestamp_sec: float = Field(default=0.0, ge=0.0, description="Offset timestamp when question was posed")
    browser_telemetry: BrowserActivityTelemetry = Field(default_factory=BrowserActivityTelemetry)
    acoustic_telemetry: AcousticIntegrityTelemetry = Field(default_factory=AcousticIntegrityTelemetry)
    visual_telemetry: VisualIntegrityTelemetry = Field(default_factory=VisualIntegrityTelemetry)
    # Day 48 Behavioral Integration Bridge
    day48_cognitive_deliberation_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Deliberation ratio from Day 48 model")
    day48_neurodiversity_safeguard_active: bool = Field(default=False, description="Whether candidate has neurodiverse gaze safeguard")


class IntegrityFlag(BaseModel):
    """Individual flagged incident of anomalous or unauthorized behavior."""
    flag_id: str = Field(description="Unique identifier for the flag incident")
    signal_type: MalpracticeSignalType = Field(description="Type of malpractice signal detected")
    severity: FlagSeverity = Field(description="Severity classification")
    detection_rule: str = Field(description="Rule name or heuristic trigger (e.g. THRESHOLD_TAB_SWITCH)")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence of the detection")
    turn_index: int = Field(ge=1, description="Turn index where incident occurred")
    evidence_details: str = Field(description="Human-interpretable explanation of the anomaly")


class RealTimeWarningAlert(BaseModel):
    """Notification dispatched to candidate interface or proctoring dashboard."""
    alert_tier: AlertTierLevel = Field(description="Current warning escalation tier")
    title: str = Field(description="Header title of the warning alert")
    message: str = Field(description="User-facing guidance or warning message")
    requires_acknowledgment: bool = Field(default=False, description="Whether candidate must click acknowledge")
    escalated_to_proctor: bool = Field(default=False, description="Whether proctor was alerted for live review")


class TurnIntegrityScore(BaseModel):
    """Evaluated integrity assessment for a single interview turn."""
    turn_index: int = Field(ge=1)
    turn_risk_score: float = Field(ge=0.0, le=100.0, description="Risk index 0 (clean) to 100 (severe malpractice)")
    turn_integrity_index: float = Field(ge=0.0, le=100.0, description="Integrity score 100 (flawless) to 0 (compromised)")
    flags_raised: List[IntegrityFlag] = Field(default_factory=list)
    alert_dispatched: Optional[RealTimeWarningAlert] = None
    deliberation_exemption_applied: bool = Field(default=False, description="True if looking away was exonerated via Day 48 deliberation")


class IntegrityEvaluationReportFormat(BaseModel):
    """Standardized audit dossier format for complete interview integrity evaluation (Deliverable 3)."""
    report_id: str = Field(description="Unique report identifier")
    candidate_id: str = Field(description="Candidate identifier")
    session_id: str = Field(description="Interview session identifier")
    target_role: str = Field(description="Target engineering role")
    session_risk_tag: InterviewRiskTag = Field(description="High-level risk classification")
    overall_integrity_score: float = Field(ge=0.0, le=100.0, description="Overall integrity score 0.0 to 100.0")
    total_incidents_count: int = Field(ge=0, description="Total count of verified flags raised")
    critical_incidents_count: int = Field(ge=0, description="Count of critical severity flags")
    highest_warning_tier: AlertTierLevel = Field(description="Max alert tier reached during session")
    turn_assessments: List[TurnIntegrityScore] = Field(default_factory=list)
    verified_malpractice_patterns: List[str] = Field(default_factory=list)
    exonerated_behavioral_events: List[str] = Field(default_factory=list)
    auditor_action_recommendation: str = Field(description="Guidance for recruiting / hiring manager")
    audit_integrity_hash: str = Field(description="SHA-256 cryptographic provenance digest")
