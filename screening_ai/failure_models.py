"""
Day 31: Edge Case & Failure Handling Models
============================================
Pydantic schemas and enums defining telephonic failure conditions:
- Poor Audio (SNR, Clipping, Packet Loss, Whisper, Low Bitrate)
- Background Noise (Stationary Hum, Traffic, Babble, Keyboard)
- Language Mixing (Hinglish Code-Switching, Entity Normalization)
- Missing Answers (Silence, Empty Fillers, Evasive Deflections)
- Diagnostic Retry & Clarification Logic
- Multi-Tier Safety Fallbacks & Emergency Human Handoffs
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class AudioDegradationType(str, Enum):
    """Types of acoustic signal degradation commonly encountered on phone lines."""
    NORMAL = "NORMAL"
    LOW_AMPLITUDE_WHISPER = "LOW_AMPLITUDE_WHISPER"
    CLIPPING_DISTORTION = "CLIPPING_DISTORTION"
    PACKET_LOSS_BURST = "PACKET_LOSS_BURST"
    LOW_BITRATE_CODEC = "LOW_BITRATE_CODEC"


class NoiseEnvironmentType(str, Enum):
    """Acoustic environmental background noise categories."""
    QUIET = "QUIET"
    STATIONARY_HUM = "STATIONARY_HUM"           # Air conditioner, fans, electrical hum
    TRAFFIC_HONKING = "TRAFFIC_HONKING"         # Street, outdoor, vehicular horn spikes
    OFFICE_BABBLE = "OFFICE_BABBLE"             # Cafeteria chatter, competing speech
    KEYBOARD_TYPING = "KEYBOARD_TYPING"         # Mechanical switch clicks, tapping
    DYNAMIC_SPIKE = "DYNAMIC_SPIKE"             # Door slam, dog barking, baby crying


class LanguageMixingCategory(str, Enum):
    """Categorization of bilingual or multilingual language mixing."""
    MONOLINGUAL_ENGLISH = "MONOLINGUAL_ENGLISH"
    HINGLISH_CODE_SWITCH = "HINGLISH_CODE_SWITCH"      # Mixed Hindi/English sentence structure
    BILINGUAL_TECHNICAL = "BILINGUAL_TECHNICAL"        # English technical nouns in regional syntax
    REGIONAL_IDIOMATIC = "REGIONAL_IDIOMATIC"          # Regional phrasing and transliterated numbers


class MissingAnswerType(str, Enum):
    """Categories of empty or uninformative responses."""
    COMPLETE_SILENCE = "COMPLETE_SILENCE"              # No speech energy detected
    EMPTY_FILLER = "EMPTY_FILLER"                      # Pure acoustic fillers ('uh', 'hello?', 'can you hear me?')
    EXPLICIT_PASS = "EXPLICIT_PASS"                    # "I don't know", "Pass", "Next question"
    EVASIVE_DEFLECTION = "EVASIVE_DEFLECTION"          # Answers something completely unrelated/dodges


class ClarificationAction(str, Enum):
    """Specific diagnostic clarification actions based on failure root cause."""
    ACOUSTIC_REPEAT = "ACOUSTIC_REPEAT"                # "The audio connection dipped, could you repeat..."
    ENVIRONMENTAL_RETRY = "ENVIRONMENTAL_RETRY"        # "There is background noise on the line..."
    SEMANTIC_DISAMBIGUATION = "SEMANTIC_DISAMBIGUATION"# "Could you clarify if buyout is approved..."
    SIMPLIFIED_ALTERNATE = "SIMPLIFIED_ALTERNATE"      # "Let's rephrase: have you used Redis in production?"
    POLITE_SKIP = "POLITE_SKIP"                        # "No problem, let's move to the next topic..."
    HUMAN_ESCALATION = "HUMAN_ESCALATION"              # "Routing to human recruiter due to persistent interference"


class SafetyDegradationTier(str, Enum):
    """Degradation modes ensuring fail-safe conversation execution."""
    NORMAL_FLOW = "NORMAL_FLOW"                        # Standard full conversational screening
    SIMPLIFIED_QUESTIONING = "SIMPLIFIED_QUESTIONING"  # Shorter, direct single-concept questions
    STRUCTURED_VERIFICATION = "STRUCTURED_VERIFICATION"# Binary (yes/no) or multiple choice fallback
    EMERGENCY_HUMAN_HANDOFF = "EMERGENCY_HUMAN_HANDOFF"# Failsafe routing to senior recruiter
    SAFE_TERMINATION = "SAFE_TERMINATION"              # Polite session teardown with saved audit packet


class FailureSeverity(str, Enum):
    """Severity of the detected conversational failure."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AudioTelemetry(BaseModel):
    """Acoustic metrics captured per speech segment."""
    snr_db: float = Field(28.0, description="Signal-to-Noise Ratio in decibels (clean >= 20dB)")
    peak_amplitude_dbfs: float = Field(-12.0, description="Peak signal level in dBFS (-30 to -3)")
    packet_loss_rate: float = Field(0.0, description="RTP packet loss percentage (0.0 to 1.0)")
    clipping_events: int = Field(0, description="Count of saturated sample spikes (>= -0.5 dBFS)")
    codec_bitrate_kbps: float = Field(64.0, description="Audio codec bitrate in kbps")
    estimated_noise_type: NoiseEnvironmentType = NoiseEnvironmentType.QUIET
    estimated_audio_degradation: AudioDegradationType = AudioDegradationType.NORMAL
    acoustic_confidence_discount: float = Field(0.0, description="Confidence deduction applied (0.0 to 0.40)")


class CodeSwitchResult(BaseModel):
    """Result of language-mixing detection and canonical normalization."""
    original_utterance: str
    detected_category: LanguageMixingCategory
    detected_languages: List[str] = Field(default_factory=lambda: ["en"])
    hindi_token_count: int = 0
    english_token_count: int = 0
    normalized_english_text: str
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 1.0


class MissingAnswerAssessment(BaseModel):
    """Assessment of silence or evasive non-answers."""
    duration_ms: int = 0
    word_count: int = 0
    filler_token_ratio: float = 0.0
    is_silence: bool = False
    is_empty_filler: bool = False
    is_explicit_pass: bool = False
    is_evasive: bool = False
    category: MissingAnswerType = MissingAnswerType.COMPLETE_SILENCE
    recovery_tier: int = 1
    recovery_prompt: Optional[str] = None


class RetryDecision(BaseModel):
    """Decision output by the diagnostic retry and clarification engine."""
    action: ClarificationAction
    attempt_number: int = 1
    max_attempts: int = 2
    retry_budget_remaining: int = 1
    prompt_message: str
    escalation_required: bool = False
    severity: FailureSeverity = FailureSeverity.LOW


class SafetyHandoffPacket(BaseModel):
    """Immutable audit trail for human recruiter escalation and ATS syncing."""
    session_id: str
    candidate_id: str
    timestamp: str
    degradation_tier: SafetyDegradationTier
    reason: str
    unresolved_failures: List[str] = Field(default_factory=list)
    turns_completed: int = 0
    partial_score: Optional[float] = None
    audio_summary: Dict[str, Any] = Field(default_factory=dict)
    transcript_snapshot: List[Dict[str, Any]] = Field(default_factory=list)


class ResilientTurnResult(BaseModel):
    """Unified result for an edge-case evaluated screening turn."""
    turn_id: int
    original_text: str
    normalized_text: str
    audio_telemetry: AudioTelemetry
    code_switch_result: CodeSwitchResult
    missing_answer_result: Optional[MissingAnswerAssessment] = None
    retry_decision: Optional[RetryDecision] = None
    safety_tier: SafetyDegradationTier = SafetyDegradationTier.NORMAL_FLOW
    is_safe_to_advance: bool = True
    system_response: str
    audit_flags: List[str] = Field(default_factory=list)
