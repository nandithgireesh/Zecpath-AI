from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SpeakerType(str, Enum):
    BOT = "BOT"
    CANDIDATE = "CANDIDATE"
    SYSTEM = "SYSTEM"


class CallStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DROPPED = "DROPPED"
    FAILED = "FAILED"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"          # >= 0.85
    MEDIUM = "MEDIUM"      # 0.70 - 0.84
    LOW = "LOW"            # 0.50 - 0.69
    CRITICAL_LOW = "CRITICAL_LOW" # < 0.50


class WordConfidence(BaseModel):
    word: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None


class TranscriptTurn(BaseModel):
    turn_id: str
    speaker: SpeakerType = SpeakerType.CANDIDATE
    raw_text: str
    normalized_text: Optional[str] = None
    start_time_ms: int = Field(default=0, ge=0)
    end_time_ms: int = Field(default=0, ge=0)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    word_confidences: List[WordConfidence] = Field(default_factory=list)
    audio_segment_url: Optional[str] = None
    is_low_confidence: bool = False


class ExtractedEntities(BaseModel):
    experience_years: Optional[float] = None
    skills_confirmed: List[str] = Field(default_factory=list)
    notice_period_days: Optional[int] = None
    is_immediate_joiner: Optional[bool] = None
    current_ctc_lpa: Optional[float] = None
    expected_ctc_lpa: Optional[float] = None
    ctc_negotiable: Optional[bool] = None
    current_location: Optional[str] = None
    relocation_willingness: Optional[bool] = None
    remote_preferred: Optional[bool] = None
    highest_degree: Optional[str] = None
    raw_entities: Dict[str, Any] = Field(default_factory=dict)


class QuestionInteractionRecord(BaseModel):
    interaction_id: str
    question_id: str
    category: str = "General"
    prompt_text: str
    response_raw: str
    response_normalized: Optional[str] = None
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    extracted_entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    validation_status: str = "VALID"  # VALID, INVALID, CLARIFICATION_NEEDED


class CallMetadata(BaseModel):
    candidate_id: str
    candidate_name: Optional[str] = "Candidate"
    job_id: str
    role_name: Optional[str] = "General Role"
    call_id: str
    session_id: Optional[str] = None
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: float = Field(default=0.0, ge=0.0)
    audio_format: str = "wav"
    sample_rate: int = 16000
    language: str = "en"
    avg_confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    call_status: CallStatus = CallStatus.COMPLETED


class VoiceTranscriptPayload(BaseModel):
    session_id: str
    metadata: CallMetadata
    turns: List[TranscriptTurn] = Field(default_factory=list)
    question_interactions: List[QuestionInteractionRecord] = Field(default_factory=list)
    full_raw_text: Optional[str] = ""
    full_normalized_text: Optional[str] = ""


class NormalizedScreeningData(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    role_name: str
    evaluation_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    overall_audio_quality: Dict[str, Any] = Field(default_factory=dict)
    extracted_profile: ExtractedEntities
    category_evaluations: Dict[str, Any] = Field(default_factory=dict)
    readiness_for_scoring: bool = True
    full_normalized_dialogue: str = ""


class NormalizationResult(BaseModel):
    raw_text: str
    cleaned_text: str
    removed_fillers: List[str] = Field(default_factory=list)
    normalized_entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.HIGH
    is_low_confidence: bool = False
