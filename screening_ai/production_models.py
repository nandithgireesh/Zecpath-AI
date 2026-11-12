"""
screening_ai/production_models.py
Day 32: Screening System Finalization

Pydantic data schemas for the production screening orchestrator,
session state, multi-modal turn payloads, system health, and handover manifest.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ProductionSessionConfig(BaseModel):
    """Configuration for initializing an end-to-end production screening call."""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    candidate_name: str = Field(..., description="Full name of the candidate")
    job_role: str = Field(default="Senior Python Engineer", description="Target job profile")
    target_experience_years: float = Field(default=3.0, description="Minimum required experience")
    max_budget_lpa: float = Field(default=30.0, description="Upper CTC budget in LPA")
    max_notice_days: int = Field(default=60, description="Maximum acceptable notice period in days")
    required_skills: List[str] = Field(
        default_factory=lambda: ["Python", "FastAPI", "PostgreSQL", "Docker", "Microservices"],
        description="Mandatory technical skills"
    )
    apply_threshold_optimization: bool = Field(
        default=True,
        description="Enable Brevity Protection and Hesitation Dampening to prevent false rejections"
    )
    enable_acoustic_fairness_buffer: bool = Field(
        default=True,
        description="Enable acoustic confidence discounting for poor phone lines"
    )
    enable_hinglish_normalization: bool = Field(
        default=True,
        description="Enable automatic code-switching normalization for Indian recruitment context"
    )


class ScreeningTurnInput(BaseModel):
    """Multi-modal inbound candidate turn payload."""
    turn_index: int = Field(default=1, description="Sequential index of the conversational turn")
    candidate_speech: str = Field(..., description="Spoken transcript utterance from candidate")
    snr_db: float = Field(default=22.0, description="Signal-to-Noise ratio in dB")
    amplitude_dbfs: float = Field(default=-18.0, description="Audio peak/RMS amplitude in dBFS")
    packet_loss_rate: float = Field(default=0.0, description="RTP packet loss rate (0.0 to 1.0)")
    clipping_events: int = Field(default=0, description="Count of amplitude saturation clipping events")
    response_time_seconds: float = Field(default=2.5, description="Latency before candidate began speaking")


class ScreeningTurnOutput(BaseModel):
    """Outbound turn response produced by the ProductionScreeningSystem."""
    turn_index: int = Field(..., description="Sequential turn index")
    current_state: str = Field(..., description="Active state machine state")
    ai_spoken_prompt: str = Field(..., description="Next prompt to synthesize and play to candidate")
    detected_intent: Optional[str] = Field(None, description="Classified intent category")
    normalized_speech: Optional[str] = Field(None, description="Cleaned/translated English utterance")
    extracted_entities: Dict[str, Any] = Field(default_factory=dict, description="Parsed entities")
    acoustic_discount: float = Field(default=0.0, description="Fairness discount applied for degraded line")
    safety_tier: str = Field(default="NORMAL_FLOW", description="Safety degradation tier")
    is_terminal: bool = Field(default=False, description="Whether conversation reached terminal state")
    is_escalated: bool = Field(default=False, description="Whether session tripped circuit breaker")


class ProductionScreeningSession(BaseModel):
    """Complete stateful production screening session record."""
    session_id: str = Field(..., description="Unique UUID for this screening session")
    config: ProductionSessionConfig = Field(..., description="Session configuration")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="ACTIVE", description="Session lifecycle status")
    current_state: str = Field(default="CALL_INITIATED", description="FSM state")
    turn_count: int = Field(default=0, description="Total turns processed")
    turns: List[Dict[str, Any]] = Field(default_factory=list, description="Historical turn log")
    eligibility_passed: Optional[bool] = Field(None, description="Hard-gate eligibility check result")
    overall_score: Optional[float] = Field(None, description="Calibrated final screening score (0-100)")
    final_decision: Optional[str] = Field(None, description="Hiring decision band")
    report_summary: Optional[Dict[str, Any]] = Field(None, description="Structured executive report")
    handoff_packet: Optional[Dict[str, Any]] = Field(None, description="Human escalation audit packet if tripped")


class ProductionSubsystemStatus(BaseModel):
    """Health check status for an individual screening subsystem."""
    subsystem_name: str
    status: str = "HEALTHY"
    latency_ms: float = 0.0
    details: Optional[str] = None


class ProductionSystemHealth(BaseModel):
    """System-wide diagnostic readiness and health response."""
    status: str = "HEALTHY"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    version: str = "1.0.0-prod"
    uptime_status: str = "OPERATIONAL"
    subsystems: List[ProductionSubsystemStatus] = Field(default_factory=list)
    active_sessions_count: int = 0


class ProductionHandoverManifest(BaseModel):
    """Engineering handover manifest inventorying all production modules."""
    track_title: str = "Zecpath-AI Voice Screening Engine (Days 21-32)"
    completion_date: str = "2026-09-20"
    author: str = "Nandith Gireesh"
    organization: str = "Zecser Business LLP"
    repository: str = "Zecpath-AI"
    total_curriculum_days: int = 12
    modules_inventory: List[Dict[str, Any]] = Field(default_factory=list)
    metrics_summary: Dict[str, Any] = Field(default_factory=dict)
    api_endpoints_count: int = 0
    test_suites_count: int = 0
