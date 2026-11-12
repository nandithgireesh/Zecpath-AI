"""
Day 59: API & Integration Planning - Data Models & Request/Response Schemas
===========================================================================
Platform: Zecpath Enterprise Automated Hiring Platform
Defines strict Pydantic models and serialization contracts for:
1. Resume Parsing API (Async)
2. ATS Scoring API (Async/Hybrid)
3. Screening AI API (Sync/WebSocket)
4. Interview AI API (Sync/Streaming)
5. Decision AI API (Sync/Hybrid)
Plus Authentication, Idempotency, Rate Limiting, and RFC-7807 Error Envelopes.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
import time
import uuid


class ProcessingMode(str, Enum):
    SYNC = "SYNC"
    ASYNC = "ASYNC"
    STREAMING = "STREAMING"


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AuthScheme(str, Enum):
    BEARER_JWT = "BEARER_JWT"
    API_KEY = "API_KEY"
    HMAC_SHA256 = "HMAC_SHA256"


# =============================================================================
# 1. AUTHENTICATION & SECURITY MODELS
# =============================================================================
class APIAuthContext(BaseModel):
    tenant_id: str = Field(..., description="Enterprise client identifier")
    user_id: str = Field(..., description="Authenticated recruiter or system service ID")
    roles: List[str] = Field(default_factory=lambda: ["recruiter"])
    scopes: List[str] = Field(default_factory=lambda: ["ai:read", "ai:write"])
    auth_scheme: AuthScheme = AuthScheme.BEARER_JWT
    expires_at: float = Field(default_factory=lambda: time.time() + 3600.0)


# =============================================================================
# 2. STANDARDIZED RFC-7807 ERROR ENVELOPE
# =============================================================================
class APIErrorDetail(BaseModel):
    code: str
    message: str
    target: Optional[str] = None


class APIErrorEnvelope(BaseModel):
    type: str = "https://api.zecpath.ai/errors/bad-request"
    title: str = "Validation or Processing Error"
    status: int = 400
    detail: str
    instance: str
    timestamp: float = Field(default_factory=time.time)
    errors: List[APIErrorDetail] = Field(default_factory=list)


# =============================================================================
# 3. RESUME PARSING API (ASYNC)
# =============================================================================
class ResumeParseRequest(BaseModel):
    candidate_id: str = Field(..., description="Unique candidate ID")
    document_url: str = Field(..., description="Pre-signed S3/GCS secure document URL")
    mime_type: str = Field("application/pdf", description="Document MIME type (pdf/docx)")
    webhook_callback_url: Optional[str] = Field(None, description="Async completion notification webhook")
    extract_academic_profile: bool = True
    anonymize_pii: bool = True


class ExtractedSkill(BaseModel):
    name: str
    years_experience: float
    confidence: float


class ResumeParseResult(BaseModel):
    candidate_id: str
    full_name: Optional[str] = None
    email_redacted: str
    skills: List[ExtractedSkill]
    experience_years: float
    education_level: str
    cleaned_text_preview: str
    parsing_latency_ms: float


class AsyncJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: float = Field(default_factory=time.time)
    estimated_completion_seconds: float = 2.5
    status_url: str
    result: Optional[ResumeParseResult] = None
    error: Optional[str] = None


# =============================================================================
# 4. ATS SCORING API (ASYNC/HYBRID)
# =============================================================================
class ATSScoreRequest(BaseModel):
    job_id: str = Field(..., description="Requisition Job Identifier")
    candidate_id: str = Field(..., description="Candidate Identifier")
    job_description_text: str = Field(..., min_length=20, description="Full job description")
    candidate_resume_text: str = Field(..., min_length=20, description="Extracted resume text")
    required_skills: List[str] = Field(default_factory=list)
    min_experience_years: float = 2.0


class ATSScoreResponse(BaseModel):
    candidate_id: str
    job_id: str
    composite_ats_score: float = Field(..., ge=0.0, le=100.0)
    skill_match_score: float
    experience_fit_score: float
    formatting_hygiene_score: float
    matched_skills: List[str]
    missing_critical_skills: List[str]
    is_shortlisted: bool
    evaluation_timestamp: float = Field(default_factory=time.time)


# =============================================================================
# 5. SCREENING AI API (SYNC / WEBSOCKET)
# =============================================================================
class ScreeningSessionRequest(BaseModel):
    candidate_id: str
    job_id: str
    role_title: str
    max_duration_minutes: int = 15


class ScreeningUtteranceRequest(BaseModel):
    session_id: str
    candidate_id: str
    turn_index: int
    transcript_utterance: str
    audio_latency_ms: float = 120.0
    is_silence: bool = False


class ScreeningUtteranceResponse(BaseModel):
    session_id: str
    turn_index: int
    ai_next_question: str
    detected_intent: str
    eligibility_status: str  # "PASS", "FLAGGED", "FAIL"
    is_session_complete: bool
    turn_processing_latency_ms: float


# =============================================================================
# 6. INTERVIEW AI API (SYNC / REAL-TIME STREAMING)
# =============================================================================
class InterviewTurnRequest(BaseModel):
    interview_session_id: str
    candidate_id: str
    current_topic: str
    candidate_answer_text: str
    code_submission: Optional[str] = None
    voice_pitch_variance: float = 14.5
    speech_rate_wpm: float = 142.0
    turn_index: int


class InterviewTurnResponse(BaseModel):
    interview_session_id: str
    turn_index: int
    turn_technical_score: float
    turn_behavioral_score: float
    realtime_pacing_feedback: Optional[str] = None
    ai_follow_up_prompt: str
    socratic_hint: Optional[str] = None
    sync_processing_latency_ms: float


# =============================================================================
# 7. DECISION AI API (SYNC / HYBRID)
# =============================================================================
class DecisionArbitrationRequest(BaseModel):
    candidate_id: str
    job_id: str
    ats_score: float = Field(..., ge=0.0, le=100.0)
    screening_score: float = Field(..., ge=0.0, le=100.0)
    hr_behavioral_score: float = Field(..., ge=0.0, le=100.0)
    technical_code_score: float = Field(..., ge=0.0, le=100.0)
    variance_damping_enabled: bool = True
    enforce_tech_floor: bool = True


class DecisionArbitrationResponse(BaseModel):
    candidate_id: str
    final_composite_score: float
    recommendation_verdict: str  # "STRONG_HIRE", "HIRE", "HOLD_REVIEW", "REJECT"
    confidence_level: float
    applied_safeguards: List[str]
    four_fifths_parity_check: str
    arbitration_timestamp: float = Field(default_factory=time.time)
