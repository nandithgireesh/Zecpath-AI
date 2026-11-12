"""
Day 36: Confidence & Stress Indicators Data Models
===================================================
Defines structured Pydantic models, Enums, and scoring schemas for:
1. Hesitation patterns (long pauses, repeated words, uncertainty phrases)
2. Sentiment analysis & emotional tone
3. Contradiction patterns (within-turn and cross-turn)
4. Stress indicators & composite stress index
5. Consolidated behavioral confidence scoring (0-100) & recruitment tiers
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class HesitationType(str, Enum):
    """Categorization of vocal and transcript hesitation signals."""
    LONG_PAUSE = "LONG_PAUSE"
    REPEATED_WORD = "REPEATED_WORD"
    UNCERTAINTY_PHRASE = "UNCERTAINTY_PHRASE"
    FALSE_START = "FALSE_START"
    DISFLUENCY_CLUSTER = "DISFLUENCY_CLUSTER"


class HesitationSignal(BaseModel):
    """Specific hesitation incident identified within candidate utterance."""
    type: HesitationType = Field(..., description="Category of hesitation detected")
    token_or_phrase: str = Field(..., description="Exact word or phrase triggering signal")
    char_offset: int = Field(0, description="Character offset in utterance")
    duration_seconds: Optional[float] = Field(None, description="Pause duration if applicable")
    penalty: float = Field(0.0, description="Deduction applied from hesitation sub-score")
    description: str = Field(..., description="Human-readable explanation of hesitation")


class SentimentPolarity(str, Enum):
    """High-level sentiment classification."""
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"


class SentimentTone(str, Enum):
    """Fine-grained emotional tone observed in professional interview discourse."""
    ENTHUSIASTIC = "ENTHUSIASTIC"
    COMPOSED_OPTIMISTIC = "COMPOSED_OPTIMISTIC"
    MATTER_OF_FACT = "MATTER_OF_FACT"
    ANXIOUS_HESITANT = "ANXIOUS_HESITANT"
    DEFENSIVE_GUARDED = "DEFENSIVE_GUARDED"
    FRUSTRATED = "FRUSTRATED"


class SentimentTurnScore(BaseModel):
    """Comprehensive sentiment analysis result for an individual interview turn."""
    polarity: SentimentPolarity = Field(SentimentPolarity.NEUTRAL, description="Coarse sentiment classification")
    compound_score: float = Field(0.0, ge=-1.0, le=1.0, description="Normalized valence (-1.0 negative to +1.0 positive)")
    positive_score: float = Field(0.0, ge=0.0, le=1.0, description="Positive sentiment probability")
    neutral_score: float = Field(1.0, ge=0.0, le=1.0, description="Neutral sentiment probability")
    negative_score: float = Field(0.0, ge=0.0, le=1.0, description="Negative sentiment probability")
    composure_score: float = Field(80.0, ge=0.0, le=100.0, description="Emotional composure score (0-100, 100=calm)")
    emotional_tone: SentimentTone = Field(SentimentTone.MATTER_OF_FACT, description="Fine-grained professional demeanor")
    positive_cues: List[str] = Field(default_factory=list, description="Positive keywords and enthusiastic phrases matched")
    negative_cues: List[str] = Field(default_factory=list, description="Defeatist or dissatisfied keywords matched")
    defensive_cues: List[str] = Field(default_factory=list, description="Defensive, reluctant, or evasive phrases matched")


class ContradictionSeverity(str, Enum):
    """Severity weighting for detected contradiction incidents."""
    NONE = "NONE"
    MILD_REVISION = "MILD_REVISION"
    DIRECT_CONTRADICTION = "DIRECT_CONTRADICTION"
    CRITICAL_INCONSISTENCY = "CRITICAL_INCONSISTENCY"


class ContradictionIncident(BaseModel):
    """Record of conflicting claims within turn or across turns."""
    severity: ContradictionSeverity = Field(..., description="Severity level of the inconsistency")
    contradiction_type: str = Field(..., description="Type of contradiction (e.g. SELF_NEGATION, TIMELINE_CLASH)")
    claim_a: str = Field(..., description="First statement or established claim")
    claim_b: str = Field(..., description="Conflicting statement or retraction")
    turn_a: Optional[int] = Field(None, description="Turn index of first claim")
    turn_b: int = Field(..., description="Turn index of conflicting statement")
    confidence_deduction: float = Field(0.0, description="Score penalty assessed")
    explanation: str = Field(..., description="Recruiter explanation of the contradiction")


class StressLevel(str, Enum):
    """Categorization of candidate stress and tension level."""
    LOW = "LOW"             # Calm, steady, and composed
    MODERATE = "MODERATE"   # Typical interview nervousness, controlled
    HIGH = "HIGH"           # Marked anxiety, hesitation clustering
    CRITICAL = "CRITICAL"   # Acute fluster, severe cognitive overload


class StressIndicators(BaseModel):
    """Quantitative measurement of stress, tension, and emotional pressure."""
    stress_index: float = Field(0.0, ge=0.0, le=100.0, description="Composite stress score (0=calm, 100=acute stress)")
    stress_level: StressLevel = Field(StressLevel.LOW, description="Categorized stress band")
    hesitation_frequency_per_100w: float = Field(0.0, description="Hesitations normalized per 100 words")
    repetition_cluster_count: int = Field(0, description="Number of stutter/repetition clusters")
    defensive_spike_detected: bool = Field(False, description="Whether defensive markers spiked under questioning")
    anxiety_markers: List[str] = Field(default_factory=list, description="Detected anxiety and uncertainty markers")
    stress_resilience_score: float = Field(100.0, ge=0.0, le=100.0, description="Candidate resilience under stress (100 - stress_index)")


class ConfidenceTier(str, Enum):
    """Executive recruiter confidence classification tiers."""
    AUTHORITATIVE = "Authoritative"   # 85.0 - 100.0: Decisive, confident, fluent
    COMPOSED = "Composed"             # 70.0 - 84.9: Professional, steady, minor hesitations
    HESITANT = "Hesitant"             # 50.0 - 69.9: Frequent uncertainty, visible hesitation
    HIGH_STRESS = "High Stress"       # < 50.0: Flustered, contradictions, defensive demeanor


class TurnConfidenceBreakdown(BaseModel):
    """Full confidence and emotional signal evaluation for an interview turn."""
    turn_index: int = Field(..., description="Turn index being evaluated")
    confidence_score: float = Field(0.0, ge=0.0, le=100.0, description="Final composite confidence score (0-100)")
    confidence_tier: ConfidenceTier = Field(ConfidenceTier.COMPOSED, description="Categorized confidence tier")
    hesitation_score: float = Field(100.0, ge=0.0, le=100.0, description="Hesitation sub-score (0-100, 100=fluent)")
    sentiment_score: float = Field(80.0, ge=0.0, le=100.0, description="Composure & sentiment sub-score (0-100)")
    consistency_score: float = Field(100.0, ge=0.0, le=100.0, description="Logical consistency sub-score (0-100)")
    stress_index: float = Field(0.0, ge=0.0, le=100.0, description="Stress index (0-100, 0=calm)")
    hesitations: List[HesitationSignal] = Field(default_factory=list, description="Specific hesitation incidents detected")
    sentiment: SentimentTurnScore = Field(default_factory=SentimentTurnScore, description="Detailed sentiment breakdown")
    contradictions: List[ContradictionIncident] = Field(default_factory=list, description="Contradictions identified in this turn")
    stress: StressIndicators = Field(default_factory=StressIndicators, description="Turn stress indicators")
    behavioral_summary: str = Field("", description="Synthesis note for recruiters")
    key_strengths: List[str] = Field(default_factory=list, description="Demonstrated behavioral confidence strengths")
    risk_flags: List[str] = Field(default_factory=list, description="Identified behavioral risk signals or coaching areas")


class SessionConfidenceSummary(BaseModel):
    """Consolidated session-level confidence and stress profile for ATS export."""
    average_confidence_score: float = Field(0.0, ge=0.0, le=100.0, description="Session-wide mean confidence score")
    overall_confidence_tier: ConfidenceTier = Field(ConfidenceTier.COMPOSED, description="Dominant confidence classification")
    average_stress_index: float = Field(0.0, ge=0.0, le=100.0, description="Session-wide mean stress index")
    overall_stress_level: StressLevel = Field(StressLevel.LOW, description="Session-wide stress classification")
    overall_hesitation_score: float = Field(100.0, ge=0.0, le=100.0, description="Mean hesitation discipline")
    overall_consistency_score: float = Field(100.0, ge=0.0, le=100.0, description="Mean narrative consistency")
    dominant_emotional_tone: SentimentTone = Field(SentimentTone.MATTER_OF_FACT, description="Primary emotional demeanor")
    total_hesitations_detected: int = Field(0, description="Total hesitation events across all turns")
    total_contradictions_detected: int = Field(0, description="Total contradictions identified in session")
    recruiter_behavioral_summary: str = Field("", description="Executive behavioral summary for ATS dossier")
