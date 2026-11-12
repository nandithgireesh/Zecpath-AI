from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AccentType(str, Enum):
    INDIAN_ENGLISH = "INDIAN_ENGLISH"
    US_ENGLISH = "US_ENGLISH"
    UK_ENGLISH = "UK_ENGLISH"
    REGIONAL_MALAYALAM = "REGIONAL_MALAYALAM"
    REGIONAL_TAMIL = "REGIONAL_TAMIL"
    REGIONAL_HINDI = "REGIONAL_HINDI"


class NoiseCondition(str, Enum):
    CLEAN_STUDIO = "CLEAN_STUDIO"           # SNR > 30 dB
    OFFICE_BACKGROUND = "OFFICE_BACKGROUND" # SNR 15 - 25 dB
    TRAFFIC_AMBIENT = "TRAFFIC_AMBIENT"     # SNR 5 - 15 dB
    LOW_GAIN_MIC = "LOW_GAIN_MIC"           # Low amplitude / muffled


class SpeechEdgeCaseType(str, Enum):
    NORMAL = "NORMAL"
    INTERRUPTED_SPEECH = "INTERRUPTED_SPEECH"
    PARTIAL_ANSWER = "PARTIAL_ANSWER"
    SILENCE_DETECTED = "SILENCE_DETECTED"
    OVERLAPPING_SPEECH = "OVERLAPPING_SPEECH"


class STTAudioMetadata(BaseModel):
    duration_seconds: float = Field(default=0.0, ge=0.0)
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"
    snr_db: float = Field(default=28.0)
    detected_noise_condition: NoiseCondition = NoiseCondition.CLEAN_STUDIO
    silence_duration_seconds: float = Field(default=0.0, ge=0.0)


class STTTranscriptionResult(BaseModel):
    raw_transcript: str
    cleaned_transcript: str
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    word_confidences: List[Dict[str, Any]] = Field(default_factory=list)
    detected_accent: AccentType = AccentType.INDIAN_ENGLISH
    audio_metadata: STTAudioMetadata = Field(default_factory=STTAudioMetadata)
    latency_ms: float = Field(default=120.0)


class SpeechEdgeCaseAnalysis(BaseModel):
    edge_case: SpeechEdgeCaseType = SpeechEdgeCaseType.NORMAL
    is_interrupted: bool = False
    is_partial: bool = False
    is_silence: bool = False
    missing_required_entities: List[str] = Field(default_factory=list)
    recovery_prompt: Optional[str] = None


class CleanTranscriptResult(BaseModel):
    original_text: str
    cleaned_text: str
    removed_fillers: List[str] = Field(default_factory=list)
    punctuation_corrected: bool = False
    proper_case_applied: bool = False
    edge_case_analysis: SpeechEdgeCaseAnalysis = Field(default_factory=SpeechEdgeCaseAnalysis)


class AccuracyBenchmarkRecord(BaseModel):
    test_id: str
    ground_truth: str
    hypothesis: str
    accent: AccentType
    noise_condition: NoiseCondition
    wer: float = Field(ge=0.0)  # Word Error Rate
    cer: float = Field(ge=0.0)  # Character Error Rate
    confidence: float = Field(ge=0.0, le=1.0)
    latency_ms: float = Field(ge=0.0)


class AccuracyBenchmarkReport(BaseModel):
    total_tests: int
    overall_wer: float
    overall_cer: float
    mean_confidence: float
    mean_latency_ms: float
    accent_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    noise_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "COMPLETED"
